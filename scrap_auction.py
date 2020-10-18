import re

import requests
from bs4 import BeautifulSoup

import config
import utils


# get's raw html, which later will be scraped
def get_html():
    url = "https://scrap.tf/auctions/" + config.auction_id

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


# finds the strings related to min bid and current bid. One is always 'None' while the other one always contains data
def get_current_bid_html_raw():
    soupified_html = get_html()
    min_bid = soupified_html.find('dd', class_='auc-bid auc-mar-top')
    current_bid = soupified_html.find('dd', id='auction-current-bid', class_='auc-bid')

    return str(min_bid), str(current_bid)  # why it's returned as strings, don't ask. It just works ;)


# extracts the type of bid(current/minimum) and it's value
def get_current_bid():
    minimum_bid, current_bid = get_current_bid_html_raw()
    # this ifs are the only thing that worked, so I guess it stays like this
    if minimum_bid != "None":
        bid_type = 'minimum'
        current = re.search('auc-bid auc-mar-top">(.*)</dd>', minimum_bid).group(1)

        return current, bid_type
    elif current_bid != "None":
        bid_type = 'current'
        current = re.search('"auction-current-bid">(.*)</dd>', current_bid).group(1)

        return current, bid_type


# gets the data related to the auctioned items
def get_auction_items_html_raw():
    soupified_html = get_html()
    auction_items = soupified_html.find('div', class_='auction-items')

    items_container = auction_items.find('div', class_='items-container')

    auction_items = items_container.find_all('div')

    fin_items = []
    for item in auction_items:
        fin_items.append(str(item))

    # gets item's quality(strange, unique etc.)
    qualities = []
    for fin_item in fin_items:
        filtered = re.search('item hoverable (.*) app440"', fin_item)
        if filtered is not None:
            qualities.append(filtered.group(1).split(' '))

    # gets the properties of of items
    data_contents = []
    for fin_item in fin_items:
        filtered = re.search('data-content="(.*)" style=', fin_item)
        if filtered is not None:
            data_contents.append(filtered.group(1))
    property_lists = []
    for item in data_contents:
        property_lists.append(item.split('&lt;'))

    return property_lists, qualities


# generates a list of dictionaries of auctioned items
def get_auction_items_dict(lists_of_properties):
    items = []
    for property_list in lists_of_properties:

        # getting item lvl
        level = None
        if property_list[0] is not '':
            level = property_list[0].split(" ")[1]
        # ==================================

        # initializing properties and setting them to None, in case the HTML does not contain info regarding them
        effect = None
        slot = None
        name = None
        killstreak_level = None
        sheen = None
        spells = []
        paint = None
        is_craftable = True  # in scrap.tf html item's craftable state is only noted if it's uncraftable
        is_festive = False  # in scrap.tf html item's festive state is only noted if it's festive
        condition = None
        quality = None
        strange_parts = []
        # ==================================

        for prop in property_list:

            # getting item's name
            if 'data-title' in prop:
                data = prop.split('"')
                if data[-1] is not '':
                    name = data[-1]
                else:
                    name = property_list[property_list.index(prop) + 1].split(';')[-1]
                if '(' in name:  # getting item's condition(factory new etc.) & cutting out condition from the name
                    split = name.split('(')
                    condition = split[-1][0:-1]
                    name = split[0][0:-1]
                if 'Festive' in name:  # check if item is festive
                    is_festive = True
                if 'Taunt: ' in name:
                    name = name.split(': ')[-1]
                if 'Vintage ' in name:
                    print(name)
                    print(type(name))
                    name = name.split(' ')[1:]
                    string = ' '
                    name = string.join(name)

            # ==================================

            # getting item slot
            if 'data-slot' in prop:
                slot = re.search('data-slot="(.*)" ', prop).group(1)
            # ==================================

            # getting item effect
            if 'Effect' in prop:
                effect = re.search('Effect: (.*)', prop).group(1)
            # ==================================

            # getting item killstreak
            if 'Killstreaks Active' in prop:
                killstreak_level = prop.split(';')[-1].split(' ')
                killstreak_level = killstreak_level[0] + ' ' + killstreak_level[1]
                killstreak_level = killstreak_level[0:-1]
            # ==================================

            # getting item sheen
            if 'Sheen' in prop:
                sheen = re.search('Sheen: (.*)', prop).group(1)
            # ==================================

            # getting item spell(s)
            if 'Halloween Spell' in prop:
                spells.append(prop.split(': ')[-1])
            # ==================================

            # getting item paint
            if 'Painted' in prop:
                split = prop.split(' ')
                paint = ''
                for el in split:
                    if 'Painted' not in el:
                        paint += el + " "
                paint = paint[0:-1]
            # ==================================

            # getting item's strange parts
            if 'Strange Part' in prop:
                strange_parts.append(prop.split(': ')[-1])
            # ==================================

            # checking if item is uncraftable
            if 'Uncraftable' in prop:
                is_craftable = False
            # ==================================

            # checking if item is uncraftable
            if 'Festivized' in prop:
                is_festive = True
            # ==================================

            # getting item's strange parts
            _, qualities = get_auction_items_html_raw()
            quality = qualities[lists_of_properties.index(property_list)][0].split('quality')[1]
            # ==================================

        dict_instance = {
            'name': name,
            'level': level,
            'Craftable': is_craftable,
            'killstreak': killstreak_level,
            'sheen': sheen,
            'quality': quality,
            'quality_alt': utils.get_alt_quality(quality),
            'particle_effect': effect,
            'is_skin': None,
            'condition': condition,
            'paint': paint,
            'spell(s)': spells,
            'slot': slot,
            'part(s)': strange_parts,
            'festive': is_festive
        }
        items.append(dict_instance)
    return items
