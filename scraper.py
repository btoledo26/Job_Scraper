# import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
import httpx
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import time


class Scraper:
    def __init__(self):
        options = Options()
        options.add_argument("-headless")
        self.driver = webdriver.Firefox(options=options)
        self.proxies = []

    def gather_proxies(self) -> None:
        proxy_url = "https://sslproxies.org/"
        self.driver.get(proxy_url)
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.TAG_NAME, 'tbody')))
        table_body = self.driver.find_element(By.TAG_NAME, 'tbody')
        table_rows = table_body.find_elements(By.TAG_NAME, 'tr')

        for row in table_rows:
            ip = row.find_elements(By.TAG_NAME, 'td')[0].text
            port = row.find_elements(By.TAG_NAME, 'td')[1].text
            self.proxies.append(ip+':'+port)

        # print(self.proxies)

    def scrape_jobs(self) -> None:
        page_number = 0
        url = "https://www.indeed.com/jobs?q=software+engineer&l=Oregon&start=%s" % page_number
        self.driver.get(url)
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "jobsearch-ResultsList")))
        joblist = self.driver.find_element(By.CLASS_NAME, "jobsearch-ResultsList")
        jobs = joblist.find_elements(By.TAG_NAME, 'li')

        for job in jobs[0:1]:
            print(job.find_element(By.CLASS_NAME, "jcs-JobTitle").text)  # Title
            print(job.find_element(By.CLASS_NAME, "companyName").text)  # Company
            print(job.find_element(By.CLASS_NAME, "companyLocation").text)
            print(job.find_element(By.CLASS_NAME, "jcs-JobTitle").get_attribute('href'))

    def cleanup(self) -> None:
        self.driver.quit()


def main():
    web_scraper = Scraper()
    # web_scraper.gather_proxies()
    web_scraper.scrape_jobs()
    web_scraper.cleanup()


if __name__ == "__main__":
    main()
