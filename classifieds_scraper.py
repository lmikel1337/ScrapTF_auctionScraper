from selenium import webdriver
import time
import re
from bs4 import BeautifulSoup

import config


def create_url(item_name, param, particle_id=None):
    item_name = item_name.replace(' ', '%20').replace(':', '%3A')
    if param == 'unusual':
        url = f'https://backpack.tf/unusual/{item_name}'
    elif param == 'unusual_classifieds':
        url = f'https://backpack.tf/classifieds?item={item_name}&quality=5&tradable=1&craftable=1&australium=-1&particle={particle_id}&killstreak_tier=0'

    return url


def get_effects_info(browser_driver, unusuals_name):
    url = create_url(unusuals_name, param='unusual')
    browser_driver.get(url)

    html = browser_driver.page_source.split('</div>')

    effects = []
    number_in_existence = []
    bp_prices = []

    for line in html:
        if 'data-effect_id=' in line:
            tmp = re.search('data-effect_id="(.*)" data-exist', line)
            if tmp:
                effects.append(tmp.group(1))
        if 'data-exist=' in line:
            tmp = re.search('data-exist="(.*)" data-original-title', line)
            if tmp:
                number_in_existence.append(tmp.group(1))
        if 'data-p_bptf' in line:
            tmp = re.search('data-p_bptf="(.*) keys" data', line)
            if tmp:
                bp_prices.append(tmp.group(1))
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
            price = price.group(1).split('"')[0].replace(' keys', '').replace(' ref', '').replace(' ', '')
            price = convert_currency(price, key_price)
        # if price == '':
        #     price = re.search('data-listing_mp_price="(.*)"', line)
        #     if price:
        #         price = price.group(1).split('"')[0]
        intent = re.search('listing-intent-(.*)">', line)
        if intent:
            if intent.group(1) == 'buy':
                bo_listings_counter += 1
                bo_prices.append(price)
            elif intent.group(1) == 'sell':
                so_listings_counter += 1
                so_prices.append(price)
    return bo_prices, so_prices, bo_listings_counter, so_listings_counter


def get_current_key_price(browser_driver, param='metal'):
    browser_driver.get('https://backpack.tf/stats/Unique/Mann%20Co.%20Supply%20Crate%20Key/Tradable/Craftable')
    souped_html = BeautifulSoup(browser_driver.page_source, 'html.parser')
    classifieds = souped_html.findAll("li", {"class": "listing"})
    html_lines = []
    for item in classifieds:
        html_lines.append(str(item))
    for line in html_lines:
        intent = re.search('listing-intent-(.*)">', line)
        if intent:
            if intent.group(1) == 'buy':
                if param == 'metal':
                    price = re.search('data-listing_price="(.*)"', line)
                elif param == 'usd':
                    price = re.search('data-p_bptf_all="(.*)"', line)

                if price:
                    current_key_val = price.group(1).split('"')[0].replace(' keys', '').replace(' ref', '').replace(' ', '').replace('$', '').replace('key', '')

                    return current_key_val


def convert_currency(currency_val_to_convert, current_key_price):
    if currency_val_to_convert is not '' and currency_val_to_convert is not None:
        if '–' in currency_val_to_convert:
            currency_val_to_convert = currency_val_to_convert.split('–')[0]
            # return float(currency_val_to_convert)
        if '$' in currency_val_to_convert:
            currency_val_to_convert = currency_val_to_convert.replace('$', '')
            currency_val_to_convert = float(currency_val_to_convert) / float(current_key_price[1])
            return round(currency_val_to_convert, 2)
        if ',' not in currency_val_to_convert:
            return float(currency_val_to_convert)

        currency_val_to_convert = currency_val_to_convert.split(',')
        currency_val_to_convert[0] = float(currency_val_to_convert[0])
        currency_val_to_convert[1] = float(currency_val_to_convert[1])

        currency_val_to_convert[1] = currency_val_to_convert[1] / float(current_key_price[0])
        return round(currency_val_to_convert[0] + currency_val_to_convert[1], 2)


def kowalski_analyze(
        browser_driver, item_name, item_info, buy_orders, sell_orders, classified_url, current_key_price):
    item_info[1] = convert_currency(item_info[1], current_key_price)

    quickbuy_coefficient = -1

    if buy_orders[0] is not None and item_info[1] is not None:
        traders_coefficient = buy_orders[0][0] / float(item_info[1])
    else:
        traders_coefficient = -1
    if not sell_orders[0]:
        sell_orders[0] == 0
    if sell_orders[0] and buy_orders[0] and sell_orders[0] is not None and len(sell_orders[0]) != 0:
        # print(f'sell_orders[0]: {sell_orders[0]}')
        # print(f'buy_orders[0]: {buy_orders[0]}')
        if sell_orders[0][0] is not None and sell_orders[0][0]:
            quickbuy_coefficient = buy_orders[0][0] / sell_orders[0][0]

    if quickbuy_coefficient >= 1:
        print(item_name)
        print(f'url: {classified_url}')
        print(f'bo_count: {buy_orders[1]}\nbo_prices: {buy_orders[0]}')
        print(f'bp price: {item_info[1]}')
        print(f'quickbuy_coefficient: {quickbuy_coefficient}')
        print(f'traders_coefficient: {traders_coefficient}')


def scrape_unusuals(browser_driver, list_of_items):

    current_key_price = [get_current_key_price(browser_driver), get_current_key_price(browser_driver, param='usd')]
    for item in reversed(list_of_items):
        item_effects = get_effects_info(browser_driver, item)
        for i in range(0, len(item_effects['unusual_effect_ids'])):

            current_effect = item_effects['unusual_effect_ids'][i]
            current_bp_price = item_effects['bp_prices'][i]

            url = create_url(item, param='unusual_classifieds', particle_id=current_effect)
            bo_prices, so_prices, bo_listings_counter, so_listings_counter = get_listings(browser_driver, url, current_key_price)

            kowalski_analyze(
                browser_driver,
                item,
                [current_effect, current_bp_price],
                [bo_prices, bo_listings_counter],
                [so_prices, so_listings_counter],
                url,
                current_key_price
            )


def get_item_lists(browser_driver, search_mode, ignore_taunts):
    if search_mode == 'unusual_hats_taunts':
        browser_driver.get('https://backpack.tf/unusuals')

        html = browser_driver.page_source.split('</div>')
        items = []
        for line in html:
            if 'data-name=' in line:
                tmp = re.search('data-base_name="(.*)" data-app', line)
                if tmp:
                    if not ignore_taunts:
                        items.append(tmp.group(1))
                    else:
                        if 'Taunt' not in tmp.group(1):
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


def scrape_coordinator(mode='unusual_hats_taunts', ignore_taunts=False):
    driver = get_driver(driver_type='Firefox')
    login(driver)

    if 'unusual' in mode:
        unusuals = get_item_lists(driver, mode, ignore_taunts)
        scrape_unusuals(driver, unusuals)


scrape_coordinator(mode='unusual_hats_taunts', ignore_taunts=True)
