import time
import datetime
from selenium import webdriver
from bs4 import BeautifulSoup

import re

import config


def get_raffle_ids(browser_driver):
    print('ID acquisition started...')
    driver = browser_driver
    driver.get("https://scrap.tf/raffles")
    driver = scroll_on_page(driver)

    print('acquiring raffle ids...')
    html = driver.page_source.split('</div>')
    raffles_ids = []
    for div in html:
        if 'class="panel-raffle "' in div:
            if 'class="raffle-name"' in div:
                raffle_id = re.search('href="/raffles/(.*)">', div).group(1)
                raffles_ids.append(raffle_id[0:6])
    print('raffle ids acquired')
    return raffles_ids


def scroll_on_page(driver):
    print('Starting scrolling...')
    scroll_pause_time = 1
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    print('Scrolling completed')
    return driver


def get_joined_raffle_limit(html):
    pass


def get_driver(driver_type='firefox'):
    driver_type = driver_type.lower()
    if driver_type == 'firefox':
        driver = webdriver.Firefox(executable_path=config.FIREFOX_DRIVER_PATH)
    return driver


def get_raffled_items(souped_html):
    items_html = str(souped_html.findAll("div", {"class": "items-container"})).split('</div>')
    fin_items = []
    for item_html in items_html:

        quality = re.search('item hoverable (.*) ', item_html)
        slot = re.search('data-slot="(.*)" ', item_html)

        if quality:
            quality = quality.group(1).split(' ')[0]
        else:
            quality = None
        if slot:
            slot = slot.group(1).split(' ')[0].replace('\'', '').replace('"', '').replace(' ', '')
        else:
            slot = None
        fin_items.append([slot, quality])

    return fin_items


def join_raffle_decider(souped_html):
    raffle_items = get_raffled_items(souped_html)
    should_join = False
    for raffle_item in raffle_items:
        if raffle_item[0] not in config.join_raffle_decider_blacklist_slot and raffle_item[0] is not None:
            should_join = True
        else:
            if raffle_item[1] not in config.join_raffle_decider_blacklist_quality and raffle_item[1] is not None:
                should_join = True
    return should_join


def login():
    print('started login process...')
    driver = get_driver(driver_type='Firefox')
    driver.get("https://scrap.tf/login")
    input('Type anything when the login process is done: ')
    return driver


def join_raffles(mode='one_time', loop_delay=10):
    print(f'running in {mode} mode')

    driver = login()

    if mode == 'one_time':
        iter_count = 1
    elif mode == 'loop':
        iter_count = 999999

    total_raffles_joined_in_session = 0
    raffle_id_blacklist = []

    for i in range(0, iter_count):
        timer_start = datetime.datetime.now()

        joined_raffles_in_cycle_counter = 0

        print('Checking for new raffles...')
        raffle_ids = get_raffle_ids(driver)
        print(type(raffle_ids))
        print(f'raffle_ids {raffle_ids}')
        for id in raffle_ids:
            if id in raffle_id_blacklist:
                print(f'removed {id}')
                try:
                    raffle_ids = raffle_ids.remove(id)
                except:
                    pass

        if not raffle_ids:
            print(f'No new raffles found\nnext check in {loop_delay} min({(datetime.datetime.now() + datetime.timedelta(minutes=loop_delay)).strftime("%H:%M:%S")})')
            time.sleep(loop_delay * 60)
        else:
            print(f'found {len(raffle_ids)} new raffles')

            print(f'Total active raffles: {format(len(raffle_ids))}')
            print('started the process of joining the raffles...')
            print('______________________________________')

            for raffle_id in raffle_ids:
                raffle_index = raffle_ids.index(raffle_id) + 1
                print(f"{raffle_index}. opening raffle {raffle_id}")
                url = "https://scrap.tf/raffles/{0}".format(raffle_id)
                driver.get(url)
                souped_html = BeautifulSoup(driver.page_source, 'html.parser')

                button_found = False
                for xpath in config.scraptf_raffle_join_button_xpaths:
                    try:
                        button = driver.find_element_by_xpath(xpath)
                        button_found = True
                        break
                    except Exception:
                        button_found = False
                        # print('Raffle already button_found...\nRaffle joining process stopped...')
                        # print_summary(mode, scheduled_start_time, joined_raffles_in_cycle_counter, timer_start, i)
                if button_found:
                    should_join_raffle = join_raffle_decider(souped_html)
                    if should_join_raffle:
                        print(should_join_raffle)
                        button.click()
                        joined_raffles_in_cycle_counter += 1
                        print(f"raffle {raffle_id} joined")
                    else:
                        raffle_id_blacklist.append(raffle_id)
                        print(f'raffle {raffle_id} not joined, reason: not_enough_value')
                else:
                    print(f'Raffle {raffle_id} could not be button_found')

                time.sleep(3)

        total_raffles_joined_in_session += joined_raffles_in_cycle_counter

        print_summary(total_raffles_joined_in_session, joined_raffles_in_cycle_counter, timer_start, i)
    driver.quit()
# /html/body/div[5]/div/div[3]/div[7]/div[2]/button[2]


def print_summary(total_raffles_joined_in_session, joined_raffles_in_cycle_counter, timer_start, cycle_index):
    print('______________________________________')
    print(f'timestamp: {datetime.datetime.now().strftime("%H:%M:%S")}')
    print(f'Cycle number: {cycle_index+1}')
    print(f'Total raffles joined: {total_raffles_joined_in_session}')
    print(f'Joined raffles in current cycle: {joined_raffles_in_cycle_counter}')
    print(f'Cycle work time: {datetime.datetime.now()}')
    print('______________________________________')



# raffle_items = [['secondary', 'quality6']]
# for raffle_item in raffle_items:
#     should_join = False
#     print(raffle_item[0])
#     print(raffle_item[1])
#     if raffle_item[0] not in config.join_raffle_decider_blacklist_slot:
#         should_join = True
#     else:
#         if raffle_item[1] not in config.join_raffle_decider_blacklist_quality:
#             should_join = True
#     print(should_join)

# raffle_ids ['2R4HRD', 'G06QXG', 'FW56R0', 'TSAQ96', 'V1PY9D', 'UL8ZQL', '006VRD', 'R3B7Z6', '2V77BZ', 'S7FVYK', '8Z4RGW', 'CHFMAT', '7IV04C', 'UYV317']
# found 14 new raffles

# raffle_ids ['2R4HRD', 'G06QXG', 'FW56R0', 'TSAQ96', 'V1PY9D', 'UL8ZQL', '006VRD', 'R3B7Z6', '2V77BZ', 'S7FVYK', '8Z4RGW', 'CHFMAT', '7IV04C', 'UYV317']
