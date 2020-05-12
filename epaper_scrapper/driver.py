import os
import urllib.request
from urllib.error import HTTPError

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from epaper_scrapper.image_utils import superimpose, merge, build_pdf

# Absolute paths
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
CHROME_DRIVER_PATH = os.path.join(ROOT_DIR, 'bin', 'chromedriver')
OUT_DIR = os.path.join(ROOT_DIR, 'out')

# Latest Tarun Bharat Goan Edition URL
TB_URL = 'https://epaper.tarunbharat.com/t/505/latest/Tarun-Bharat-Goa'

# XPATHs
XPATH_IMG = '/html/body/div[7]/div[3]/div[2]/div/div[1]/div[3]/img'
XPATH_TOTAL_PAGES = '/html/body/div[7]/div[1]/div[1]/div[3]/div/input'


class Driver(object):
    """"""
    def __init__(self):
        """Initialises headless chrome driver"""
        print("Initialising chrome driver")
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
        self.url = ""

    def get_total_pages(self):
        """Fetches the total number of pages in the epaper"""
        self.driver.get(TB_URL)
        element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, XPATH_TOTAL_PAGES)))
        total_pages = int(element.get_attribute('max'))

        return total_pages

    def download_page(self, page_no):
        """Downloads the epaper image bits of the required page and merges them to form the final page image"""
        KNOWN_RES = ['1600x2626-800x875', '1600x2602-800x867', '1600x2585-800x861']
        print("Downloading page", page_no)
        myElem = None
        self.driver.get(f'{self.url}#page/{page_no}/1')

        try:
            myElem = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, XPATH_IMG)))
        except TimeoutException:
            print("Loading took too much time!")
            exit(-1)

        url = myElem.get_attribute('src').split('=')[-1].split('/')
        PAGE_DIR = os.path.join(OUT_DIR, f'page-{page_no}')
        if not os.path.exists(PAGE_DIR):
            os.makedirs(PAGE_DIR)

        for i in range(1, 3):
            for j in range(1, 4):
                for RES in KNOWN_RES:
                    img_url = f'https://cache.epapr.in/{url[3]}/{url[4]}/{RES}/{i}x{j}.jpg'
                    if fetch_image(img_url, os.path.join(PAGE_DIR, f'{i}x{j}.jpg')):
                        img_url = f'https://cache.epapr.in/{url[3]}/{url[4]}/{RES}/{i}x{j}.png'
                        if fetch_image(img_url, os.path.join(PAGE_DIR, f'{i}x{j}.png')):
                            superimpose(os.path.join(PAGE_DIR, f'{i}x{j}.jpg'),
                                        os.path.join(PAGE_DIR, f'{i}x{j}.png'),
                                        os.path.join(PAGE_DIR, f'{i}x{j}.jpg'))
                            os.path.join(PAGE_DIR, f'{i}x{j}.png')
                            break
                        break
        merge(PAGE_DIR)

    def download_latest_epaper(self):
        """Downloads all the pages of the latest epaper and binds them into a pdf"""
        self.url = fetch_latest_epaper_url()
        print("Latest epaper URL:", self.url)
        total_pages = self.get_total_pages()
        print('Total Pages:', total_pages)
        for i in range(1, total_pages + 1):
            self.download_page(i)
        build_pdf(OUT_DIR, total_pages)

    def quit(self):
        self.driver.quit()


def fetch_latest_epaper_url():
    """Fetches the latest epaper ID"""
    resp = requests.get(TB_URL)
    return resp.url.split('#')[0]


def fetch_image(img_url, file_name):
    """Downloads the image from the url and saves it with the provided filename"""
    try:
        print(img_url)
        urllib.request.urlretrieve(img_url, file_name)
        return True
    except HTTPError:
        return False
