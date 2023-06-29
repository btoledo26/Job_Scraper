import os.path
import csv
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait as Wait
import pandas as pd
import time


class Scraper:
    def __init__(self):
        options = Options()
        options.add_argument("-headless")
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-infobars')
        self.driver = webdriver.Firefox(options=options)
        self.proxies = []
        self.filepath = "jobListings.csv"

    def scrape(self) -> None:
        self.write_csv_header()

        # add all scrape functions here
        self.scrape_indeed()

        self.remove_duplicates()
        self.cleanup()

    def use_proxy(self) -> None:
        self.__gather_proxies()
        # set up proxy server rotation
        pass

    def __gather_proxies(self) -> None:
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

    def __scroll_down_page(self, speed=8):
        current_scroll_position, new_height = 0, 1
        while current_scroll_position <= new_height:
            current_scroll_position += speed
            self.__driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
            new_height = self.__driver.execute_script("return document.body.scrollHeight")

    # TODO: Set to private when complete
    def scrape_indeed(self) -> None:
        page_number = 0
        url = "https://www.indeed.com/jobs?q=software+engineer&l=Oregon&start=%s" % page_number
        self.driver.get(url)

        # self.driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")

        #WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jcs-JobTitle")))
        #WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "companyName")))
        #WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "jobTitle")))
        #WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "jobTitle")))
        #WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "/html/body/main/div/div[1]/div/div/div[5]/div[1]/div[5]/div/ul/li[1]/div/div[1]/div/div[1]/div/table[1]/tbody/tr/td/div[1]/h2")))
        # Get initial list of names
        job_listings = Wait(self.driver, 15).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'jobTitle')))

        joblist = self.driver.find_element(By.CLASS_NAME, "jobsearch-ResultsList")
        jobs = joblist.find_elements(By.TAG_NAME, 'li')

        print(len(jobs))
        rows = []
        for job in jobs[:10]:
            job_title = job.find_element(By.CLASS_NAME, "jobTitle").text
            company = job.find_element(By.CLASS_NAME, "companyName").text
            location = job.find_element(By.CLASS_NAME, "companyLocation").text
            url = job.find_element(By.CLASS_NAME, "jcs-JobTitle").get_attribute('href')

            rows.append(['', job_title, company, location, url])

            print(job_title)  # Title
            print(company)  # Company
            print(location)
            print(url)

        file = open(self.filepath, 'a', newline='')
        write = csv.writer(file, dialect='excel')
        write.writerows(rows)
        file.close()

    # TODO: Set to private when complete
    def write_csv_header(self) -> None:
        # checks if file exists before writing headers
        if not os.path.isfile(self.filepath):
            print('writing headers')
            col_names = ['Applied',
                         'Job Title',
                         'Company Name',
                         'Company Location',
                         'URL']
            f = open(self.filepath, 'w', newline='')
            writer = csv.writer(f, dialect='excel')
            writer.writerow(col_names)
            f.close()

    # TODO: Set to private when complete
    def remove_duplicates(self) -> None:
        df = pd.read_csv(self.filepath)
        df.drop_duplicates(inplace=True)
        df.to_csv(self.filepath, index=False)

    # TODO: Set to private when complete
    def cleanup(self) -> None:
        self.driver.quit()


def main():
    web_scraper = Scraper()
    # web_scraper.gather_proxies()
    web_scraper.write_csv_header()
    web_scraper.scrape_indeed()

    web_scraper.remove_duplicates()
    web_scraper.cleanup()


if __name__ == "__main__":
    main()
