import logging
import time
from csv import writer
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree as et


def scrape(driver, job_search_keyword, location_search_keyword) -> None:
    print('Scraping...')

    # add all scrape functions here
    scrape_indeed(driver, job_search_keyword, location_search_keyword)
    # scrape_glassdoor(driver, job_search_keyword, location_search_keyword)

    print('Scraping Complete')


def scrape_indeed(driver, job_search_keyword, location_search_keyword) -> None:
    print('Scraping Indeed.com...')

    indeed_base_url = 'https://www.indeed.com'
    indeed_pagination_url = "https://www.indeed.com/jobs?q={}&l={}&radius=35&start={}"

    # Open a CSV file to write the job listings data
    with open('indeed_jobs.csv', 'w', newline='', encoding='utf-8') as f:
        file_writer = writer(f)
        heading = ['URL', 'Job Title', 'Company Name', 'Location', 'Salary', 'Job Type',
                   'Searched Job', 'Searched Location']
        file_writer.writerow(heading)

        # Scrape data from pages, 0-based indexing
        all_jobs = []
        for page_no in range(0, 11):  # TODO: pull number of pages and use for range
            url = indeed_pagination_url.format(job_search_keyword, location_search_keyword, page_no)
            page_dom = __get_dom(driver, url)
            jobs = page_dom.xpath('//div[@class="job_seen_beacon"]')
            all_jobs = all_jobs + jobs
            time.sleep(5)

        # Organize data and write it to file
        for job in all_jobs:
            job_link = indeed_base_url + __get_indeed_job_link(job)
            time.sleep(2)
            job_title = __get_indeed_job_title(job)
            time.sleep(2)
            company_name = __get_indeed_company_name(job)
            time.sleep(2)
            company_location = __get_indeed_company_location(job)
            time.sleep(2)
            salary = __get_indeed_salary(job)
            time.sleep(2)
            job_type = __get_indeed_job_type(job)
            time.sleep(2)
            record = [job_link, job_title, company_name, company_location, salary, job_type,
                      job_search_keyword, location_search_keyword]
            print(record)
            file_writer.writerow(record)

    __remove_duplicates('indeed_jobs.csv')
    print('Finished scraping Indeed.com')


def scrape_glassdoor(driver, job_search_keyword, location_search_keyword) -> None:
    print('Scraping Glassdoor.com...')

    glassdoor_base_url = 'https://www.glassdoor.com'
    # glassdoor_pagination_url = 'https://www.glassdoor.com/Job/{}-{}-jobs-SRCH_IL.0,6_IS3163_KO7,24_IP{}.htm'

    # Site has semi-random urls, using hard-coded values for now
    urls = [
        'https://www.glassdoor.com/Job/oregon-software-engineer-jobs-SRCH_IL.0,6_IS3163_KO7,24.htm?includeNoSalaryJobs=true',
        'https://www.glassdoor.com/Job/oregon-software-engineer-jobs-SRCH_IL.0,6_IS3163_KO7,24_IP2.htm?includeNoSalaryJobs=true&pgc=AB4AAYEAHgAAAAAAAAAAAAAAAgik1rkAOgEBAQc7ryf1%2FLE0RCdD9KqNWWmG6wJuapjXX%2BxaMef0Bre9tdWb1ZAQ%2BOMaIRF98ZjoGsn3i4McmqUAAA%3D%3D'
        #'https://www.glassdoor.com/Job/oregon-software-engineer-jobs-SRCH_IL.0,6_IS3163_KO7,24_IP3.htm?includeNoSalaryJobs=true&pgc=AB4AAoEAPAAAAAAAAAAAAAAAAgik1rkAVAEDAQcSBg4Na704hH503YQFZm%2FKgW6fF0H432wC0s7m6bbQgOdlV5HVG9dErW5nx5zxNpvqMssukBNVKQsUjMHtUdl5FNbBDWdDvCxDDK8NIpLCdgAA',
        #'https://www.glassdoor.com/Job/oregon-software-engineer-jobs-SRCH_IL.0,6_IS3163_KO7,24_IP4.htm?includeNoSalaryJobs=true&pgc=AB4AA4EAWgAAAAAAAAAAAAAAAgik1rkAcQECAQ8gEAZ%2FHzybenWzvqh1hJOOofPAdKFRSyBBXwSxDoExaTxkPfH9O%2F7ZIYIxUWrGPr4HVOUUs7yh0OEmy7wIGRimVKx%2Fqks4dg9%2BsV6aSvtlu4r5bPxu%2F%2BSaLWBQ67J%2BMP71Lu5dIW0przs6BEqNAAA%3D',
        #'https://www.glassdoor.com/Job/oregon-software-engineer-jobs-SRCH_IL.0,6_IS3163_KO7,24_IP5.htm?includeNoSalaryJobs=true&pgc=AB4ABIEAeAAAAAAAAAAAAAAAAgik1rkAfgEEAQ8gEC4GHgcB2ILgyQ3ttCpulyUVwWUH8fqvssk0Op1j%2F1on9%2BgjYlKQ2I66y3pICwYCnZu7E0K4iuEVEZ%2BVN8JgmmjcjtXYfq7KcpOi54gMCXG4UA0R%2FBAPHXgh4SYYHwpZf0nv8aI%2FKBKGR1AWX0LqfMRV8qrRmtmiOgAA',
        #'https://www.glassdoor.com/Job/oregon-software-engineer-jobs-SRCH_IL.0,6_IS3163_KO7,24_IP6.htm?includeNoSalaryJobs=true&pgc=AB4ABYEAlgAAAAAAAAAAAAAAAgik1rkAhAEDAR9EEiYJE3ZIk9fKmUFbbxfyVc1HmbDpfBrG3rsoZEh4ng0eI%2FupJDKIyCB7YYtbVqcKoVZ8FS9YXj9NpRRG2Cy0lrcG3eCNvr4H5juoKax%2FNcAsEbNAsiLGp7%2BAvFdOCOU%2BY9T0FogxFXRb508JpCDAJRTtUX44mxgth%2F32nnoxQAAA',
        #'https://www.glassdoor.com/Job/oregon-software-engineer-jobs-SRCH_IL.0,6_IS3163_KO7,24_IP7.htm?includeNoSalaryJobs=true&pgc=AB4ABoEAtAAAAAAAAAAAAAAAAgik1rkAiAEDAR9AHpoBBiwiJrcB9xpc%2FQ7NAm%2FDjhnorbeCLLf2vS4ORF9JrbnImRY%2Br2ZLDZ%2FYMXHvfMFlDG0UekCVytAnMGXwMnNHCeRjkmTjcGuC2f0Ob9lNkx3jh8P1VSDTmtdpFRmtX8H2w0NhoTWEQ4Z6FGyjI7dRpU7q5nv0090shK9ExjNeW%2BMAAA%3D%3D'
        ]

    # Open a CSV file to write the job listings data
    with open('glassdoor_jobs.csv', 'w', newline='', encoding='utf-8') as f:
        file_writer = writer(f)
        heading = ['URL', 'Job Title', 'Company Name', 'Location', 'Salary', 'Searched Job', 'Searched Location']
        file_writer.writerow(heading)

        all_jobs = []
        for url in urls:  # site seems to list duplicates after 6th page
            page_dom = __get_dom(driver, url)
            jobs = page_dom.xpath('//div[@class="job-search-3x5mv1"]')
            all_jobs = all_jobs + jobs
            time.sleep(5)

        # Organize data and write it to file
        for job in all_jobs:
            job_link = glassdoor_base_url + __get_glassdoor_job_link(job)
            time.sleep(2)
            job_title = __get_glassdoor_job_title(job)
            time.sleep(2)
            company_name = __get_glassdoor_company_name(job)
            time.sleep(2)
            company_location = __get_glassdoor_company_location(job)
            time.sleep(2)
            salary = __get_glassdoor_salary(job)
            time.sleep(2)
            record = [job_link, job_title, company_name, company_location, salary,
                      job_search_keyword, location_search_keyword]
            file_writer.writerow(record)

    __remove_duplicates('glassdoor_jobs.csv')
    print('Finished scraping Glassdoor.com')


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
    df.to_csv(filepath, index=False)
