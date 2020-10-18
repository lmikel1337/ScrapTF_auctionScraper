import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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
            if len(raffle_id) == 6:
                raffles_ids.append(raffle_id)
    print('raffle ids acquired')
    print('Total: {0}'.format(len(raffles_ids)))
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


# def get_raffle_ids():
#     html = get_raffles_html()
#     print('started extracting raffle ids...')
#     raffles = html.find_elements_by_class_name("raffle-name")
#
#     raffle_ids = []
#     for raffle in raffles[0:]:
#         raffle_ids.append(re.search('<a href="/raffles/(.*)">', str(raffle)).group(1))
#     print('finished extracting raffle ids...')
#     return raffle_ids


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
    input('Type anything when the logic process is done: ')
    return driver


def join_raffles():
    driver = login()
    raffle_ids = get_raffle_ids(driver)
    print('Active raffles: {0}'.format(len(raffle_ids)))
    print('started the process of joining the raffles...')
    print(raffle_ids)
    for raffle_id in raffle_ids:
        print("{0}. opening raffle {1}".format(raffle_ids.index(raffle_id)+1, raffle_id))
        driver.get("https://scrap.tf/raffles/{0}".format(raffle_id))
        joined = False
        try:
            button = driver.find_element_by_xpath('/html/body/div[6]/div/div[3]/div[5]/div[2]/button[2]')
            joined = True
        except Exception:
            print("raffle already joined")
        if joined:
            button.click()
            print('raffle {0} joined'.format(raffle_id))
        time.sleep(2)
    print('Job\'s done')
    driver.quit()
