"""This module can be used to scrape job listing from Indeed and Glassdoor, and these listings are written to a .csv
file for later use. The sites can be scraped individually in separate function calls or together in a single function
call.

Warning: This may not work in the future as these sites implement systems to detect automated site interaction

Functions:
    scrape - writes a .csv file containing job listings to the 'output' folder
"""
import os
import logging
import time
from csv import writer
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree as et
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By


def scrape(job_search_keyword='', location_search_keyword='', glassdoor_start_url='', scrape_option=0) -> None:
    """Scrapes job listings from job board sites.

    Initializes a web driver, creates a directory for output files if it does not exist, and scrapes the desired sites
    based on the provided scrape option. The web driver is closed when the scraping is complete.

    Args:
        job_search_keyword: A job title to be used to search Indeed
        location_search_keyword: A location to search for jobs on Indeed
        glassdoor_start_url: The URL of the first page of a Glassdoor search, used to establish initial page before
            traversing pages
        scrape_option: An integer used to determine which job board sites to scrape

            - default: Scrape both Indeed and Glassdoor
            - 1: Only scrape Indeed
            - 2: Only scrape Glassdoor
    """
    # Initialize webdriver
    options = Options()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)

    # Make output folder if one does not exist
    if not os.path.exists('output'):
        os.mkdir('output')

    match scrape_option:
        case 1:
            print('Scraping Indeed...')
            __scrape_indeed(driver, job_search_keyword, location_search_keyword)
        case 2:
            print('Scraping Glassdoor...')
            __scrape_glassdoor(driver, glassdoor_start_url)
        case _:
            print('Scraping...')
            __scrape_indeed(driver, job_search_keyword, location_search_keyword)
            __scrape_glassdoor(driver, glassdoor_start_url)

    # Close web browser
    driver.quit()
    print('Scraping Complete.')


def __scrape_indeed(driver, job_search_keyword, location_search_keyword) -> None:
    """Scrape job listings from Indeed and store them in a .csv file."""
    job_search_keyword = job_search_keyword.strip().lower()
    location_search_keyword = location_search_keyword.strip().lower()
    indeed_base_url = 'https://www.indeed.com'
    indeed_pagination_url = "https://www.indeed.com/jobs?q={}&l={}"
    file_path = 'output/indeed_jobs.csv'

    # Open a CSV file to write the job listings data
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        file_writer = writer(f)
        heading = ['URL', 'Job Title', 'Company Name', 'Location', 'Salary', 'Job Type',
                   'Searched Job', 'Searched Location']
        file_writer.writerow(heading)

        all_jobs = []
        driver.get(indeed_pagination_url.format(job_search_keyword, location_search_keyword))
        while 1:
            page_dom = __get_dom(driver)
            jobs = page_dom.xpath('//div[@class="job_seen_beacon"]')
            all_jobs = all_jobs + jobs
            time.sleep(5)  # sleep call to avoid captcha or other verification

            try:
                driver.find_element(By.XPATH, '//nav/div[last()]/a').click()
            except Exception as e:
                logging.exception(e)
                break

        # Organize data and write it to file
        for job in all_jobs:
            job_link = indeed_base_url + __get_indeed_job_link(job)
            job_title = __get_indeed_job_title(job)
            company_name = __get_indeed_company_name(job)
            company_location = __get_indeed_company_location(job)
            salary = __get_indeed_salary(job)
            job_type = __get_indeed_job_type(job)
            record = [job_link, job_title, company_name, company_location, salary, job_type,
                      job_search_keyword, location_search_keyword]
            file_writer.writerow(record)

    __remove_duplicates(file_path)


def __scrape_glassdoor(driver, start_url) -> None:
    """Scrape job listings from Glassdoor and store them in a .csv file."""
    glassdoor_base_url = 'https://www.glassdoor.com'
    file_path = 'output/glassdoor_jobs.csv'

    # Open a CSV file to write the job listings data
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        file_writer = writer(f)
        heading = ['URL', 'Job Title', 'Company Name', 'Location', 'Salary']
        file_writer.writerow(heading)

        all_jobs = []
        driver.get(start_url)
        for i in range(1, 7):  # site seems to list duplicates after 6th page, so don't go past page 6
            # Check for popup, and close it if it exists
            if i == 2:
                time.sleep(5)  # this sleep call must be here to ensure page loads the popup
                try:
                    driver.find_element(By.CLASS_NAME, 'e1jbctw80').click()
                except Exception as e:
                    logging.exception(e)

            # Get page data
            page_dom = __get_dom(driver)
            jobs = page_dom.xpath('//li[contains(@class, "react-job-listing")]')
            all_jobs = all_jobs + jobs

            # Go to next page
            if i < 6:
                try:
                    next_page_button = driver.find_element(By.CLASS_NAME, 'nextButton')
                    if not next_page_button.is_enabled():
                        break
                    time.sleep(5)  # sleep call to avoid captcha or other verification
                    next_page_button.click()
                except Exception as e:
                    logging.exception(e)
                    break

        # Organize data and write it to file
        for job in all_jobs:
            job_link = glassdoor_base_url + __get_glassdoor_job_link(job)
            job_title = __get_glassdoor_job_title(job)
            company_name = __get_glassdoor_company_name(job)
            company_location = __get_glassdoor_company_location(job)
            salary = __get_glassdoor_salary(job)
            record = [job_link, job_title, company_name, company_location, salary]
            file_writer.writerow(record)

    __remove_duplicates(file_path)


def __get_dom(driver):
    """Gather the data of the current page from web driver and return it."""
    page_content = driver.page_source
    product_soup = BeautifulSoup(page_content, 'html.parser')
    dom = et.HTML(str(product_soup))
    return dom


def __get_indeed_job_link(job):
    """Extract job link from Indeed job listing and return it."""
    try:
        job_link = job.xpath('./descendant::h2/a/@href')[0]
    except Exception as e:
        job_link = 'Not available'
        logging.exception(e)
    return job_link


def __get_indeed_job_title(job):
    """Extract job title from Indeed job listing and return it."""
    try:
        job_title = job.xpath('./descendant::h2/a/span/text()')[0]
    except Exception as e:
        job_title = 'Not available'
        logging.exception(e)
    return job_title


def __get_indeed_company_name(job):
    """Extract company name from Indeed job listing and return it."""
    try:
        company_name = job.xpath('./descendant::span[@class="companyName"]/text()')[0]
    except Exception as e:
        company_name = 'Not available'
        logging.exception(e)
    return company_name


def __get_indeed_company_location(job):
    """Extract company location from Indeed job listing and return it."""
    try:
        company_location = job.xpath('./descendant::div[@class="companyLocation"]/text()')[0]
    except Exception as e:
        company_location = 'Not available'
        logging.exception(e)
    return company_location


def __get_indeed_salary(job):
    """Extract salary information from Indeed job listing and return it."""
    try:
        salary = job.xpath('./descendant::span[@class="estimated-salary"]/span/text()')
    except Exception as e:
        salary = 'Not available'
        logging.exception(e)
    if len(salary) == 0:
        try:
            salary = job.xpath('./descendant::div[@class="metadata salary-snippet-container"]/div/text()')[0]
        except Exception as e:
            salary = 'Not available'
            logging.exception(e)
    else:
        salary = salary[0]
    return salary


def __get_indeed_job_type(job):
    """Extract job type from Indeed job listing and return it."""
    try:
        job_type = job.xpath('./descendant::div[@class="metadata"]/div/text()')[0]
    except Exception as e:
        job_type = 'Not available'
        logging.exception(e)
    return job_type


def __get_glassdoor_job_link(job):
    """Extract job link from Glassdoor job listing and return it."""
    try:
        job_link = job.xpath('./descendant::a/@href')[0]
    except Exception as e:
        job_link = 'Not available'
        logging.exception(e)
    return job_link


def __get_glassdoor_job_title(job):
    """Extract job title from Glassdoor job listing and return it."""
    try:
        job_title = job.xpath('./descendant::a/div/div[2]/text()')[0]
    except Exception as e:
        job_title = 'Not available'
        logging.exception(e)
    return job_title


def __get_glassdoor_company_name(job):
    """Extract company name from Glassdoor job listing and return it."""
    try:
        company_name = job.xpath('./descendant::a/div/div[1]/div[2]/text()')[0]
    except Exception as e:
        company_name = 'Not available'
        logging.exception(e)
    return company_name


def __get_glassdoor_company_location(job):
    """Extract company location from Glassdoor job listing and return it."""
    try:
        company_location = job.xpath('./descendant::a/div/div[3]/text()')[0]
    except Exception as e:
        company_location = 'Not available'
        logging.exception(e)
    return company_location


def __get_glassdoor_salary(job):
    """Extract salary information from Glassdoor job listing and return it."""
    try:
        salary = job.xpath('./descendant::a/div/div[4]/text()')[0]
    except Exception as e:
        salary = 'Not available'
        logging.exception(e)
    return salary


def __remove_duplicates(filepath):
    """Remove duplicate job listings from the output file."""
    df = pd.read_csv(filepath)
    df.drop_duplicates(subset=['Job Title', 'Company Name'], inplace=True)
    df.to_csv(f'{filepath}', index=False)
