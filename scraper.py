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
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)

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
    indeed_base_url = 'https://www.indeed.com'
    indeed_pagination_url = "https://www.indeed.com/jobs?q={}&l={}&radius=35&start={}"

    # Open a CSV file to write the job listings data
    with open('indeed_jobs.csv', 'w', newline='', encoding='utf-8') as f:
        file_writer = writer(f)
        heading = ['URL', 'Job Title', 'Company Name', 'Location', 'Salary', 'Job Type',
                   'Searched Job', 'Searched Location']
        file_writer.writerow(heading)

        # Scrape data from pages, 0-based indexing
        all_jobs = []  # TODO: change loop to use 'next page' button, check for its existence, break when not found
        for page_no in range(0, 110, 10):  # pages are in 10s (10, 20, 30, ...)
            url = indeed_pagination_url.format(job_search_keyword, location_search_keyword, page_no)
            page_dom = __get_dom(driver, url)
            jobs = page_dom.xpath('//div[@class="job_seen_beacon"]')
            all_jobs = all_jobs + jobs
            time.sleep(5)

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

    __remove_duplicates('indeed_jobs.csv')


def scrape_glassdoor(driver, job_search_keyword, location_search_keyword) -> None:
    glassdoor_base_url = 'https://www.glassdoor.com'
    glassdoor_start_url = 'https://www.glassdoor.com/Job/{}-{}-jobs-SRCH_IL.0,6_IS3163_KO7,24.htm?clickSource=searchBox'

    # Open a CSV file to write the job listings data
    with open('glassdoor_jobs.csv', 'w', newline='', encoding='utf-8') as f:
        file_writer = writer(f)
        heading = ['URL', 'Job Title', 'Company Name', 'Location', 'Salary', 'Searched Job', 'Searched Location']
        file_writer.writerow(heading)

        # Scrape data from pages, 1-based indexing
        all_jobs = []  # TODO: change loop to go until 6 pages are scraped or 'next' button can no longer be found
        for i in range(1, 7):  # site seems to list duplicates after 6th page
            if i == 1:
                page_dom = __get_dom(driver, glassdoor_start_url.format(location_search_keyword, job_search_keyword))
            else:  # !!! Leave this code block in this order, scraping breaks otherwise !!!
                time.sleep(5)  # this sleep call must be here to ensure page loads
                page_dom = __get_dom(driver, driver.current_url)  # url unknown due to page nav via 'next page' button
                try:
                    driver.find_element(By.CLASS_NAME, 'e1jbctw80').click()  # Close popup window if it exists
                except Exception as e:
                    logging.exception(e)

            jobs = page_dom.xpath('//li[contains(@class, "react-job-listing")]')
            all_jobs = all_jobs + jobs
            time.sleep(5)

            if i != 6:  # Go to next page if not last page with unique listings
                driver.find_element(By.CLASS_NAME, 'nextButton').click()  # TODO: add check for button and break when not found

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

    __remove_duplicates('glassdoor_jobs.csv')


def __get_dom(driver, url):
    driver.get(url)
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
