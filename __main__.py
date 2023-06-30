from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from scraper import *


def main():
    # TODO: Add UI
    job_search_keyword = 'Software+Engineer'
    location_search_keyword = 'Oregon'

    options = Options()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)

    scrape(driver, job_search_keyword, location_search_keyword)

    # Close web browser
    driver.quit()


if __name__ == "__main__":
    main()
