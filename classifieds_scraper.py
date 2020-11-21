from selenium import webdriver
import datetime
import re
from bs4 import BeautifulSoup

import config
import utils


def create_url(item_name, param, particle_id=None):
    item_name = item_name.replace(' ', '%20').replace(':', '%3A')
    if param == 'unusual':
        url = f'https://backpack.tf/unusual/{item_name}'
    elif param == 'unusual_classifieds':
        url = f'https://backpack.tf/classifieds?item={item_name}&quality=5&tradable=1&craftable=1&australium=-1&particle={particle_id}&killstreak_tier=0'

    return url


def get_effects_info(browser_driver, unusuals_name, price_limits, current_key_price):
    url = create_url(unusuals_name, param='unusual')
    browser_driver.get(url)

    html = browser_driver.page_source.split('</div>')

    effects = []
    number_in_existence = []
    bp_prices = []

    for line in html:
        if 'data-effect_id=' in line:
            effect_id = re.search('data-effect_id="(.*)" data-exist', line)
        if 'data-exist=' in line:
            num_in_existence = re.search('data-exist="(.*)" data-original-title', line)
        if 'data-p_bptf' in line:
            price = re.search('data-p_bptf="(.*) keys" data', line)
            if price:
                price = price.group(1).split('"')[0].replace(' keys', '').replace(' ref', '').replace(' ', '').replace('key', '')
                price = utils.convert_currency(price, current_key_price)
                if price_limits[0] <= price <= price_limits[1]:
                    bp_prices.append(price)
                    if num_in_existence:
                        number_in_existence.append(num_in_existence.group(1))
                    if effect_id:
                        effects.append(effect_id.group(1))
        elif 'data-price="0"' in line:
            bp_prices.append(None)

    item_info = {
        'unusual_effect_ids': effects,
        'number_in_existence': number_in_existence,
        'bp_prices': bp_prices
    }
    return item_info


def get_listings(browser_driver, url, key_price):
    bo_prices = []
    so_prices = []
    bo_listings_counter = 0
    so_listings_counter = 0

    browser_driver.get(url)
    souped_html = BeautifulSoup(browser_driver.page_source, 'html.parser')
    classifieds = souped_html.findAll("li", {"class": "listing"})
    fin_items = []
    for item in classifieds:
        fin_items.append(str(item))
    for line in fin_items:
        price = re.search('data-listing_price="(.*)"', line)
        if price:
            price = price.group(1).split('"')[0].replace(' keys', '').replace(' ref', '').replace(' ', '').replace('key', '')
            price = utils.convert_currency(price, key_price)
        intent = re.search('listing-intent-(.*)">', line)
        if intent:
            if intent.group(1) == 'buy':
                bo_listings_counter += 1
                bo_prices.append(price)
            elif intent.group(1) == 'sell':
                so_listings_counter += 1
                so_prices.append(price)
    return bo_prices, so_prices, bo_listings_counter, so_listings_counter


def kowalski_analyze(
        browser_driver,
        item_name,
        item_info,
        buy_orders,
        sell_orders,
        classified_url,
        current_key_price,
        particle_effect):
    item_info[1] = utils.convert_currency(item_info[1], current_key_price)

    quickbuy_coefficient = -1
    so_ratio = -1
    traders_coefficient = -1
    lowest_so_to_bp_price = 1000

    if buy_orders[0] is not None and item_info[1] is not None:
        traders_coefficient = buy_orders[0][0] / float(item_info[1])
    if not sell_orders[0]:
        sell_orders[0] == 0
    if sell_orders[0] and buy_orders[0] and sell_orders[0] is not None and len(sell_orders[0]) != 0:
        if sell_orders[0][0] is not None and sell_orders[0][0]:
            quickbuy_coefficient = buy_orders[0][0] / sell_orders[0][0]
    if sell_orders[0] and sell_orders[0] is not None and len(sell_orders[0]) != 0:
        if len(sell_orders[0]) >= 2:
            if sell_orders[0][0] is not None and sell_orders[0][1] is not None:
                so_ratio = sell_orders[0][0] / sell_orders[0][1]
                if item_info[1] is not None:
                    lowest_so_to_bp_price = sell_orders[0][0] / item_info[1]

    if traders_coefficient >= 0.75 >= so_ratio and lowest_so_to_bp_price < 1: #  quickbuy_coefficient >= 0.75 and
        effect_name = utils.get_key(config.particles_dict, int(particle_effect))
        print(f'{effect_name} {item_name}')
        print(f'url: {classified_url}')
        print(f'bo_count: {buy_orders[1]} | bo_prices: {buy_orders[0]}')
        print(f'so_count: {sell_orders[1]} | so_count: {sell_orders[0]}')
        print(f'bp price: {item_info[1]}')
        print(f'quickbuy_coefficient: {quickbuy_coefficient}')
        print(f'traders_coefficient: {traders_coefficient}')
        print(f'lowest_so_to_bp_price: {lowest_so_to_bp_price}')
    else:
        print(datetime.datetime.now())


def scrape_unusuals(browser_driver, list_of_items, price_limits):
    current_key_price = [utils.get_current_key_price(browser_driver), utils.get_current_key_price(browser_driver, param='usd')]
    for item in reversed(list_of_items):
        item_effects = get_effects_info(browser_driver, item, price_limits, current_key_price)
        for i in range(0, len(item_effects['unusual_effect_ids'])):
            current_effect = item_effects['unusual_effect_ids'][i]
            current_bp_price = item_effects['bp_prices'][i]

            url = create_url(item, param='unusual_classifieds', particle_id=current_effect)
            bo_prices, so_prices, bo_listings_counter, so_listings_counter = get_listings(browser_driver, url,
                                                                                          current_key_price)

            kowalski_analyze(
                browser_driver,
                item,
                [current_effect, current_bp_price],
                [bo_prices, bo_listings_counter],
                [so_prices, so_listings_counter],
                url,
                current_key_price,
                current_effect
            )


def get_item_lists(browser_driver, search_mode, ignore_taunts):
    if search_mode == 'unusual_hats_taunts':
        browser_driver.get('https://backpack.tf/unusuals')
    elif search_mode == 'primary':
        browser_driver.get('https://backpack.tf/category/slot/primary')
        html = browser_driver.page_source.split('</div>')
        items = []
        for line in html:
            if 'data-name=' in line:
                tmp = re.search('data-base_name="(.*)" data-app', line)
                if tmp:
                    if not ignore_taunts:
                        items.append(tmp.group(1))
                    else:
                        if 'Taunt' not in tmp.group(1) and 'Shred Alert' not in tmp.group(1):
                            items.append(tmp.group(1))
                        else:
                            pass
        print(len(items))
        print(items)
        return items


def get_driver(driver_type='firefox'):
    driver_type = driver_type.lower()
    if driver_type == 'firefox':
        driver = webdriver.Firefox(executable_path=config.FIREFOX_DRIVER_PATH)
    return driver


def login(browser_driver):
    print('started login process...')
    browser_driver.get("https://backpack.tf/login")
    print("https://backpack.tf/login")
    input('Type anything when the login process is done: ')


def get_slots():
    pass


def scrape_coordinator(mode='unusual_hats_taunts', ignore_taunts=False, price_limits=None):
    if price_limits is None:
        price_limits = [0, 999999]
    driver = get_driver(driver_type='Firefox')
    login(driver)

    if 'unusual' in mode:
        unusuals = get_item_lists(driver, mode, ignore_taunts)
        scrape_unusuals(driver, unusuals, price_limits)
    elif 'low_tier' in mode:
        miscs = []
        taunts = []
        primary = get_item_lists(driver, search_mode='primary', ignore_taunts=ignore_taunts)
        secondary = []
        melee = []
        pda_2 = []
        building = []


scrape_coordinator(mode='low_tier', ignore_taunts=True)
# scrape_coordinator(mode='unusual_hats_taunts', ignore_taunts=True, price_limits=[11, 20])
