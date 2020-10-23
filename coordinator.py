import backpacktf_scraper
import scrap_auction
import utils
import raffle_joiner
import config


# this is where the magic happens
def start():
    print(f'version {config.version}\n')
    show_menu()

    # the main loop, note that it will break after 100 user inputs(including incorrect inputs)
    # a do-while loop is not implemented in Python and this is the next best solution I could find
    for i in range(0, 100):

        # scraping the auction if necessary
        # if need_to_get_items:
            # sets the bool to False so that the auction won't get scraped each iteration
        user_input = input()

        # attempts to cast the user_input to an int, raises an exception if not successful
        try:
            user_input = int(user_input)
        except Exception:
            print("invalid type")
            continue
        if user_input in range(1, 6):
            if config.auction_id == '':
                utils.set_auction_id_from_user()
            need_to_get_items = True
        else:
            need_to_get_items = False
        if need_to_get_items:
            items = get_items()
            need_to_get_items = False

        # case block wannabe
        if user_input == 0:
            break
        elif user_input == 1:
            browse_mode()
        elif user_input == 2:
            display_scraptf(items)
        elif user_input == 3:
            display_bptf(items)
        elif user_input == 4:
            need_to_get_items = True
            display_scraptf(items)
            display_bptf(items)
        elif user_input == 5:
            display_bid()
        elif user_input == 6:
            need_to_get_items = True
            utils.set_auction_id_from_user()
        elif user_input == 7:
            save_params(items)
        elif user_input == 8:
            user_input = input('join all raffles once(press 1) or every 60 min(press 2): ')
            if user_input == '1':
                raffle_joiner.join_raffles(mode='one_time')
            elif user_input == '2':
                raffle_joiner.join_raffles(mode='loop')


def browse_mode():
    print("Type 0 to exit the browsing mode")
    for j in range(1, 100):
        items = get_items()
        display_bptf(items)
        res = utils.set_auction_id_from_user()
        if res == 1:
            break


def save_params(items):
    print('params:\n -scrap - scrap only\n-bptf - bt data only\n-all - all data')
    flag = input('Enter param: ')
    if '-all' in flag:
        bid, bid_type = get_bids()
        utils.save_auction_info(items, backpacktf_scraper.get_stats(items), bid, bid_type)
    elif '-scrap' in flag:
        bid, bid_type = get_bids()
        utils.save_auction_info(items, bid, bid_type)
    elif '-bptf' in flag:
        utils.save_auction_info(backpacktf_scraper.get_stats(items))
    else:
        pass


# displays the result of scraping scrap.tf auction to the user
def display_scraptf(items_to_scrape):
    display_bid()
    print('________________________________________')
    print("auction items info:")

    for item_dict in items_to_scrape:
        for dicts_property in item_dict:
            print(dicts_property, ":", item_dict[dicts_property])
        print('________________________________________')


# displays the current bid
def display_bid():
    bid, bid_type = get_bids()
    print('\n________________________________________')
    print('The {0} bid is {1}'.format(bid_type, bid))


# displays the links to bp.tf classifieds listings of the auctioned items and their relevant
# properties(paint, spell(s), strange part(s))
def display_bptf(items_to_scrape):
    stats = backpacktf_scraper.get_stats(items_to_scrape)
    print('\n________________________________________')
    print('Links:')
    # print('________________________________________')
    for stat_instance in stats:
        print(f'Item: {items_to_scrape[stats.index(stat_instance)]["name"]}\nURL: {stat_instance["item_url"]}')
        if stat_instance["paint_url"] is not None:
            print('paint: {0}\nURL: {1}:'.format(items_to_scrape[stats.index(stat_instance)]["paint"], stat_instance["paint_url"]))
        if stat_instance["spells_url"] is not None:
            for spell in stat_instance["spells_url"]:
                print('spell: {0}\nURL: {1}:'.format(items_to_scrape[stats.index(stat_instance)]["spell(s)"][stat_instance['spells_url'].index(spell)], spell))
        if stat_instance["parts_url"] is not None:
            for part in stat_instance["parts_url"]:
                print('part: {0}\nURL: {1}:'.format(items_to_scrape[stats.index(stat_instance)]["part(s)"][stat_instance['parts_url'].index(part)], part))
        print('________________________________________')


# gets the info relating to the auction bid(value and whether it's a minimum bid or a current bid,
# which determines whether someone made a bid or not)
def get_bids():
    bid, bid_type = scrap_auction.get_current_bid()
    return bid, bid_type


# gets the list of dictionaries of auctioned items
def get_items():
    properties, _ = scrap_auction.get_auction_items_html_raw()
    items = scrap_auction.get_auction_items_dict(properties)
    return items


# displays the main menu
def show_menu():
    print('Select mode:')
    print('0: exit')
    print("1: browsing mode")
    print('2: scrap.tf only')
    print('3: bp.tf only')
    print("4: scrape auction page by AUC_ID and URLs to the bp.tf classified listings of the item ans it's relevant"
          " attachments")
    print('5: update the bid')
    print('6: change AUC_ID')
    print('7: save auction data')
    print('8: join all raffles')