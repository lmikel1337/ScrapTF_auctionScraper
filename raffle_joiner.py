import time
import datetime
from selenium import webdriver

import re

import config


def get_raffle_ids(browser_driver):
    print('driver No.1 started...')
    driver = browser_driver
    driver.get("https://scrap.tf/raffles")
    driver = scroll_on_page(driver)

    print('acquiring raffle ids ')
    html = driver.page_source.split('</div>')
    raffles_ids = []
    for div in html:
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
    print('Scrolling completed...')
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


def join_raffles(mode='one_time', loop_delay=20):
    print(f'running in {mode} mode')

    driver = login()

    if mode == 'one_time':
        iter_count = 1
    elif mode == 'loop':
        iter_count = 100

    scheduled_start_time = datetime.datetime.now() - datetime.timedelta(minutes=1)
    start_scraping_delay = 300

    for i in range(0, iter_count):
        while datetime.datetime.now() <= scheduled_start_time + datetime.timedelta(minutes=1):
            print('I SHLEEP')
            time.sleep(start_scraping_delay)

        joined_raffles_in_cycle_counter = 0

        raffle_ids = get_raffle_ids(driver)

        print(f'raffle_ids: {raffle_ids}')
        print(f'Total active raffles: {format(len(raffle_ids))}')
        print('started the process of joining the raffles...')

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

        timer_end = datetime.datetime.now()

        scheduled_start_time = timer_end + datetime.timedelta(minutes=loop_delay)

        print_summary(mode, scheduled_start_time, joined_raffles_in_cycle_counter, timer_start, i)
    driver.quit()


def print_summary(mode, scheduled_start_time, joined_raffles_in_cycle_counter, timer_start, cycle_index):
    print('______________________________________')
    print(f'timestamp: {datetime.datetime.now().strftime("%H:%M:%S")}')
    print(f'Joined {joined_raffles_in_cycle_counter} raffles in cycle No.{cycle_index+1}')
    print(f'Time elapsed: {datetime.datetime.now() - timer_start}')
    if mode == 'loop':
        print(
            f'next joining scheduled for {scheduled_start_time.strftime("%H:%M:%S")}')