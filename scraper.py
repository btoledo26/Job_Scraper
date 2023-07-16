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


def scrape(job_search_keyword, location_search_keyword, scrape_option=0) -> None:
    # Initialize webdriver
    options = Options()
    # options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)

    # Make output folder if one does not exist
    if not os.path.exists('output'):
        os.mkdir('output')

    match scrape_option:
        case 1:
            print('Scraping Indeed...')
            scrape_indeed(driver, job_search_keyword, location_search_keyword)
        case 2:
            print('Scraping Glassdoor...')
            scrape_glassdoor(driver, job_search_keyword, location_search_keyword)
        case _:
            print('Scraping...')
            scrape_indeed(driver, job_search_keyword, location_search_keyword)
            scrape_glassdoor(driver, job_search_keyword, location_search_keyword)

    # Close web browser
    driver.quit()
    print('Scraping Complete.')


def scrape_indeed(driver, job_search_keyword, location_search_keyword) -> None:
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

        # Scrape data from pages, 0-based indexing
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


def scrape_glassdoor(driver, job_search_keyword, location_search_keyword) -> None:
    location_search_keyword = __format_glassdoor_location_keyword(location_search_keyword)
    job_search_keyword = job_search_keyword.strip().lower()
    glassdoor_base_url = 'https://www.glassdoor.com'
    glassdoor_start_url = 'https://www.glassdoor.com/Job/{}-{}-jobs-SRCH_IL.0,11_IC1151682_KO12,16.htm'
    file_path = 'output/glassdoor_jobs.csv'

    # Open a CSV file to write the job listings data
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        file_writer = writer(f)
        heading = ['URL', 'Job Title', 'Company Name', 'Location', 'Salary', 'Searched Job', 'Searched Location']
        file_writer.writerow(heading)

        # Scrape data from pages, 1-based indexing
        all_jobs = []
        driver.get(glassdoor_start_url.format(location_search_keyword, job_search_keyword))
        for i in range(1, 7):  # site seems to list duplicates after 6th page, so don't go past page 6
            # Check for popup, and close it if it exists
            if i == 2:
                time.sleep(5)  # this sleep call must be here to ensure page loads
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
            record = [job_link, job_title, company_name, company_location, salary,
                      job_search_keyword, location_search_keyword]
            file_writer.writerow(record)

    __remove_duplicates(file_path)


def __get_dom(driver):
    page_content = driver.page_source
    product_soup = BeautifulSoup(page_content, 'html.parser')
    dom = et.HTML(str(product_soup))
    return dom


# Extract Indeed.com job link
def __get_indeed_job_link(job):
    try:
        job_link = job.xpath('./descendant::h2/a/@href')[0]
    except Exception as e:
        job_link = 'Not available'
        logging.exception(e)
    return job_link


# Extract Indeed.com job title
def __get_indeed_job_title(job):
    try:
        job_title = job.xpath('./descendant::h2/a/span/text()')[0]
    except Exception as e:
        job_title = 'Not available'
        logging.exception(e)
    return job_title


# Extract Indeed.com company name
def __get_indeed_company_name(job):
    try:
        company_name = job.xpath('./descendant::span[@class="companyName"]/text()')[0]
    except Exception as e:
        company_name = 'Not available'
        logging.exception(e)
    return company_name


# Extract Indeed.com company location
def __get_indeed_company_location(job):
    try:
        company_location = job.xpath('./descendant::div[@class="companyLocation"]/text()')[0]
    except Exception as e:
        company_location = 'Not available'
        logging.exception(e)
    return company_location


# Extract Indeed.com salary information
def __get_indeed_salary(job):
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


# Extract Indeed.com job type
def __get_indeed_job_type(job):
    try:
        job_type = job.xpath('./descendant::div[@class="metadata"]/div/text()')[0]
    except Exception as e:
        job_type = 'Not available'
        logging.exception(e)
    return job_type


# Correct the formatting of the location keyword for the URL
def __format_glassdoor_location_keyword(location_keyword):
    location_keyword = location_keyword.strip().lower()
    location_keyword = location_keyword.replace(' ', '')
    location_keyword = location_keyword.replace(',', '-')
    location_keyword += '-us'
    return location_keyword


# Extract Glassdoor.com job link
def __get_glassdoor_job_link(job):
    try:
        job_link = job.xpath('./descendant::a/@href')[0]
    except Exception as e:
        job_link = 'Not available'
        logging.exception(e)
    return job_link


# Extract Glassdoor.com job title
def __get_glassdoor_job_title(job):
    try:
        job_title = job.xpath('./descendant::a/div/div[2]/text()')[0]
    except Exception as e:
        job_title = 'Not available'
        logging.exception(e)
    return job_title


# Extract Glassdoor.com company name
def __get_glassdoor_company_name(job):
    try:
        company_name = job.xpath('./descendant::a/div/div[1]/div[2]/text()')[0]
    except Exception as e:
        company_name = 'Not available'
        logging.exception(e)
    return company_name


# Extract Glassdoor.com company location
def __get_glassdoor_company_location(job):
    try:
        company_location = job.xpath('./descendant::a/div/div[3]/text()')[0]
    except Exception as e:
        company_location = 'Not available'
        logging.exception(e)
    return company_location


# Extract Glassdoor.com salary information
def __get_glassdoor_salary(job):
    try:
        salary = job.xpath('./descendant::a/div/div[4]/text()')[0]
    except Exception as e:
        salary = 'Not available'
        logging.exception(e)
    return salary


def __remove_duplicates(filepath):
    df = pd.read_csv(filepath)
    df.drop_duplicates(subset=['Job Title', 'Company Name'], inplace=True)
    df.to_csv(f'{filepath}', index=False)
