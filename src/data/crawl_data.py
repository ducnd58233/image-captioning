import os
import time
from datetime import datetime, timezone
from io import BytesIO

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

os.chdir('..\\')
root_dir = os.getcwd() + '\\data\\space_image_captioning_dataset'
img_path = './space_image_captioning_dataset/space_images/'

images_dir = os.path.join(
    root_dir,
    'space_images'
)

captions_path = os.path.join(
    root_dir,
    'space_captions.txt'
)

os.makedirs(root_dir, exist_ok=True)
os.makedirs(images_dir, exist_ok=True)
WEBDRIVER_DELAY_TIME_INT = 2


class CrawlData:
    def __init__(self, name, logger, page_start, page_end, lock):
        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--accept-insecure-certs')

        chrome_options.headless = True

        self.name = name
        self.logger = logger
        self.page_start = page_start
        self.page_end = page_end
        self.driver = webdriver.Chrome('chromedriver', options=chrome_options)
        self.driver.implicitly_wait(4)
        self.wait = WebDriverWait(self.driver, WEBDRIVER_DELAY_TIME_INT)
        self.page_idx = page_start
        self.lock = lock

    def run(self):
        for page_idx in range(self.page_start, self.page_end):
            news_page_urls = self.get_main_page_information(page_idx)
            self.page_idx = page_idx
            for news_page_url in news_page_urls:
                self.get_news_page_information(news_page_url)
                time.sleep(WEBDRIVER_DELAY_TIME_INT)
                self.driver.back()
                time.sleep(WEBDRIVER_DELAY_TIME_INT)

    def get_main_page_information(self, page_idx):
        main_url = f'https://kienthuckhoahoc.org/kh-vu-tru/page{page_idx}'
        self.driver.get(main_url)
        news_lst_xpath = './/a[@class="title"]'
        time.sleep(WEBDRIVER_DELAY_TIME_INT)
        news_tags = self.driver.find_elements(
            By.XPATH,
            news_lst_xpath
        )

        return [news_tag.get_attribute('href') for news_tag in news_tags]

    def get_news_page_information(self, url):
        self.driver.get(url)
        img_box_xpath = './/div[@class="img-box"]/img'
        time.sleep(WEBDRIVER_DELAY_TIME_INT)
        img_box_tags = self.driver.find_elements(
            By.XPATH,
            img_box_xpath
        )

        img_box_captions_set = set()
        if img_box_tags:
            for img_box_tag in img_box_tags:
                self.get_image_information(img_box_captions_set)

    def get_image_information(self, img_box_captions_set):
        self.lock.acquire()
        try:
            img_tag = self.wait.until(
                EC.visibility_of_element_located(
                    (
                        By.TAG_NAME,
                        'img'
                    )
                )
            )

            img_caption = img_tag.get_attribute('alt')

            if img_caption not in img_box_captions_set:
                img_box_captions_set.add(img_caption)
                img_url = img_tag.get_attribute('src')

                if img_url[-3:] != 'gif' and img_caption and img_url:
                    self.save_image_information(img_url, img_caption)
                else:
                    self.logger.error(
                        f'{self.name} - Page: {self.page_idx} / {(self.page_end - 1)} - Failed to save image: Image not found')

        except Exception as e:
            self.logger.error(
                f'{self.name} - Page: {self.page_idx} / {(self.page_end - 1)} - Failed to save image: {e}')

        time.sleep(WEBDRIVER_DELAY_TIME_INT)
        self.lock.release()

    def save_image_information(self, img_url, img_caption):
        img_url_resp = requests.get(img_url)

        img = Image.open(BytesIO(img_url_resp.content))

        if img.mode == 'P':
            img = img.convert('RGB')

        img_name = f'IMG_{int(datetime.now(timezone.utc).timestamp() * 1000)}.jpg'
        img_save_path = os.path.join(images_dir, img_name)

        caption_file_line_content = img_path + img_name + '\t' + img_caption + '\n'

        with open(captions_path, 'a+', encoding='utf8') as f:
            f.write(caption_file_line_content)
            img.save(img_save_path)

            self.logger.info(
                f'{self.name} - Page: {self.page_idx} / {(self.page_end - 1)} - Success saved image: {img_name} - {img_caption}')
