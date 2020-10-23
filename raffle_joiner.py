import time
import datetime
from selenium import webdriver

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
        iter_count = 100

    total_raffles_joined_in_session = 0

    for i in range(0, iter_count):

        print('Checking for new raffles...')
        raffle_ids = get_raffle_ids(driver)
        if not raffle_ids:
            print(f'No new raffles found\nnext check in {loop_delay} min({(datetime.datetime.now() + datetime.timedelta(minutes=loop_delay)).strftime("%H:%M:%S")})')
            time.sleep(loop_delay * 60)
        else:
            print(f'found {len(raffle_ids)} new raffles')

            joined_raffles_in_cycle_counter = 0

            print(f'Total active raffles: {format(len(raffle_ids))}')
            print('started the process of joining the raffles...')
            print('______________________________________')

            timer_start = datetime.datetime.now()

            for raffle_id in raffle_ids:

                raffle_index = raffle_ids.index(raffle_id) + 1
                print(f"{raffle_index}. opening raffle {raffle_id}")

                driver.get("https://scrap.tf/raffles/{0}".format(raffle_id))

                joined = False
                try:
                    button = driver.find_element_by_xpath('/html/body/div[6]/div/div[3]/div[5]/div[2]/button[2]')
                    joined = True
                except Exception:
                    try:
                        button = driver.find_element_by_xpath('/html/body/div[6]/div/div[3]/div[7]/div[2]/button[2]')
                        joined = True
                    except Exception:
                        print('Raffle already joined...\nRaffle joining process stopped...')
                        # print_summary(mode, scheduled_start_time, joined_raffles_in_cycle_counter, timer_start, i)
                        break
                if joined:
                    button.click()
                    joined_raffles_in_cycle_counter += 1
                    print(f"raffle {raffle_id} joined")

                time.sleep(3)

        total_raffles_joined_in_session += joined_raffles_in_cycle_counter

        print_summary(total_raffles_joined_in_session, joined_raffles_in_cycle_counter, timer_start, i)
    driver.quit()


def print_summary(total_raffles_joined_in_session, joined_raffles_in_cycle_counter, timer_start, cycle_index):
    print('______________________________________')
    print(f'timestamp: {datetime.datetime.now().strftime("%H:%M:%S")}')
    print(f'total raffle joined: {total_raffles_joined_in_session}')
    print(f'Cycle: {cycle_index+1}')
    print(f'Joined raffles in current cycle: {joined_raffles_in_cycle_counter}')
    print(f'Cycle work time: {datetime.datetime.now() - timer_start}')
    print('______________________________________')
