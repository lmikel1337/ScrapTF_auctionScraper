import datetime
import re
from bs4 import BeautifulSoup

import config


# uf called, forces a user to enter a value the len of an auction id
# Note that it doesn't check whether it's a valid id, only that it has the right len
def set_auction_id_from_user():
    for j in range(0, 100):
        user_input = input("Enter AUC_ID: ")
        if user_input == '0':
            return 1
        elif len(user_input) == 6:
            config.auction_id = user_input
            print('AUC_ID set')
            break


# converts the quality id which both scrap.tf and bp.tf use to their names for easier reading
def get_alt_quality(quality):
    if quality == '11':
        return 'strange'
    elif quality == '5':
        return 'unusual'
    elif quality == '1':
        return 'genuine'
    elif quality == '6':
        return 'unique'
    elif quality == '15':
        return 'decorated weapon'
    else:
        return quality


# converts name of the killstreak tier to the id system bp.tf uses
def convert_killstreak_tier(killstreak_tier):
    if killstreak_tier is None:
        return '0'
    elif killstreak_tier == 'Basic Killstreak':
        return '1'
    elif killstreak_tier == 'Specialized Killstreak':
        return '2'
    elif killstreak_tier == 'Professional Killstreak':
        return '3'


# formats the input string by adding %20 between each word
def format_name_for_url(name):
    name = name.split(' ')
    fin_name = ''
    for word in name:
        if 'Strange' not in word:
            fin_name += word + '%20'
    return fin_name[0:-3]


def save_auction_info(items, bid, bid_type):
    file = open("info.txt", 'a')
    file.write('timestamp: {0}\n'.format(datetime.datetime.now()))
    file.write("{0} bis is {1}\n".format(bid_type, bid))
    for item in items:
        file.write('stats:\n')
        write_dict(file, items)
        file.write("------------------------------------\n")
    file.close()


def save_auction_info(stats):
    file = open("info.txt", 'a')
    file.write('timestamp: {0}\n'.format(datetime.datetime.now()))
    for item in stats:
        file.write('{0} stats:\n'.format(item['name']))
        write_dict(file, item)
        file.write("------------------------------------\n")
    file.close()


def save_auction_info(items, stats, bid, bid_type):
    file = open("info.txt", 'a')
    file.write('timestamp: {0}\n'.format(datetime.datetime.now()))
    file.write("{0} bis is {1}\n".format(bid_type, bid))
    for item in items:
        file.write('stats:\n')
        write_dict(file, item)
        file.write("------------------------------------\n")
    for item in stats:
        file.write('{0} stats:\n'.format(item['name']))
        write_dict(file, item)
        file.write("------------------------------------\n")
    file.close()


def write_dict(file, dictionary):
    for el in dictionary:
        file.write(str(el) + ": " + str(dictionary[el]) + '\n')


def get_key(dictionary, searched_val):
    for key, value in dictionary.items():
        if value == searched_val:
            return key
    return 'key doesn\'t exist'


def convert_currency(currency_val_to_convert, current_key_price):
    if isinstance(currency_val_to_convert, float):
        return currency_val_to_convert
    if currency_val_to_convert is not '' and currency_val_to_convert is not None:
        if '–' in currency_val_to_convert:
            currency_val_to_convert = currency_val_to_convert.split('–')[0]
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
                    current_key_val = price.group(1).split('"')[0].replace(' keys', '').replace(' ref', '').replace(' ','').replace('$', '')

                    return current_key_val