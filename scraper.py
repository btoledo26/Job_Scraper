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
        self.proxy_url = "https://sslproxies.org/"
        options = Options()
        options.add_argument("-headless")
        self.driver = webdriver.Firefox(options=options)
        self.proxies = []

    def gather_proxies(self) -> None:
        self.driver.get(self.proxy_url)
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.TAG_NAME, 'tbody')))
        table_body = self.driver.find_element(By.TAG_NAME, 'tbody')
        table_rows = table_body.find_elements(By.TAG_NAME, 'tr')

        for row in table_rows:
            ip = row.find_elements(By.TAG_NAME, 'td')[0].text
            port = row.find_elements(By.TAG_NAME, 'td')[1].text
            self.proxies.append(ip+':'+port)

        print(self.proxies)
        self.driver.close()

    def scrape_jobs(self) -> None:
        page_number = 0
        url = "https://www.indeed.com/jobs?q=software+engineer&l=Oregon&start=%s" % page_number

        options = Options()
        options.add_argument("-headless")

        with webdriver.Firefox(options=options) as driver:
            driver.get(url)
            joblist = driver.find_element(By.CLASS_NAME, "jobsearch-ResultsList")
            print(driver.current_url)
            print(driver.title)
            driver.close()

        jobs = joblist.find_elements(By.TAG_NAME, 'li')
        print(joblist)
        print(jobs)

        for job in jobs:
            print(job.find_element(By.CLASS_NAME, "jcs-JobTitle").text)  # Title
            print(job.find_element(By.CLASS_NAME, "companyName").text)  # Company
            print(job.find_element(By.CLASS_NAME, "companyLocation").text)
            print(job.find_element(By.CLASS_NAME, "companyName").text)
            # print(job.find_element(By.CLASS_NAME, "estimated-salary").text)

    def cleanup(self) -> None:
        self.driver.quit()


def main():
    web_scraper = Scraper()
    web_scraper.gather_proxies()

    web_scraper.cleanup()


if __name__ == "__main__":
    main()
