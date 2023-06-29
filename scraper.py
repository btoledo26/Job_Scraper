from csv import writer
from bs4 import BeautifulSoup
from lxml import etree as et
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time


class Scraper:
    def __init__(self):
        options = Options()
        options.add_argument("-headless")
        self.driver = webdriver.Firefox(options=options)
        self.filepath = 'indeed_jobs.csv'
        self.job_search_keyword = 'Software+Engineer'
        self.location_search_keyword = 'Oregon'
        self.indeed_base_url = 'https://www.indeed.com'
        self.indeed_pagination_url = "https://www.indeed.com/jobs?q={}&l={}&radius=35&start={}"

    def scrape(self) -> None:
        print('Scraping...')

        # add all scrape functions here
        self.scrape_indeed()

        print('Scraping Complete')

    def scrape_indeed(self) -> None:
        # Open a CSV file to write the job listings data
        with open(self.filepath, 'w', newline='', encoding='utf-8') as f:
            file_writer = writer(f)
            heading = ['URL', 'Job Title', 'Company Name', 'Location', 'Salary', 'Job Type', 'Rating',
                       'Job Description', 'Searched Job', 'Searched Location']
            file_writer.writerow(heading)

            all_jobs = []
            for page_no in range(0, 5):
                url = self.indeed_pagination_url.format(self.job_search_keyword, self.location_search_keyword, page_no)
                page_dom = self.__get_dom(url)
                jobs = page_dom.xpath('//div[@class="job_seen_beacon"]')
                all_jobs = all_jobs + jobs
                time.sleep(5)

            for job in all_jobs:
                job_link = self.indeed_base_url + self.__get_job_link(job)
                time.sleep(2)
                job_title = self.__get_job_title(job)
                time.sleep(2)
                company_name = self.__get_company_name(job)
                time.sleep(2)
                company_location = self.__get_company_location(job)
                time.sleep(2)
                salary = self.__get_salary(job)
                time.sleep(2)
                job_type = self.__get_job_type(job)
                time.sleep(2)
                rating = self.__get_rating(job)
                time.sleep(2)
                job_desc = self.__get_job_desc(job)
                time.sleep(2)
                record = [job_link, job_title, company_name, company_location, salary, job_type, rating,
                          job_desc, self.job_search_keyword, self.location_search_keyword]
                file_writer.writerow(record)

        # Closing the web browser
        self.driver.quit()

    def __get_dom(self, url):
        self.driver.get(url)
        page_content = self.driver.page_source
        product_soup = BeautifulSoup(page_content, 'html.parser')
        dom = et.HTML(str(product_soup))
        return dom

    # functions to extract job link
    def __get_job_link(self, job):
        try:
            job_link = job.xpath('./descendant::h2/a/@href')[0]
        except Exception as e:
            job_link = 'Not available'
        return job_link

    # functions to extract job title
    def __get_job_title(self, job):
        try:
            job_title = job.xpath('./descendant::h2/a/span/text()')[0]
        except Exception as e:
            job_title = 'Not available'
        return job_title

    # functions to extract the company name
    def __get_company_name(self, job):
        try:
            company_name = job.xpath('./descendant::span[@class="companyName"]/text()')[0]
        except Exception as e:
            company_name = 'Not available'
        return company_name

    # functions to extract the company location
    def __get_company_location(self, job):
        try:
            company_location = job.xpath('./descendant::div[@class="companyLocation"]/text()')[0]
        except Exception as e:
            company_location = 'Not available'
        return company_location

    # functions to extract salary information
    def __get_salary(self, job):
        try:
            salary = job.xpath('./descendant::span[@class="estimated-salary"]/span/text()')
        except Exception as e:
            salary = 'Not available'
        if len(salary) == 0:
            try:
                salary = job.xpath('./descendant::div[@class="metadata salary-snippet-container"]/div/text()')[0]
            except Exception as e:
                salary = 'Not available'
        else:
            salary = salary[0]
        return salary

    # functions to extract job type
    def __get_job_type(self, job):
        try:
            job_type = job.xpath('./descendant::div[@class="metadata"]/div/text()')[0]
        except Exception as e:
            job_type = 'Not available'
        return job_type

    # functions to extract job rating
    def __get_rating(self, job):
        try:
            rating = job.xpath('./descendant::span[@class="ratingNumber"]/span/text()')[0]
        except Exception as e:
            rating = 'Not available'
        return rating

    # functions to extract job description
    def __get_job_desc(self, job):
        try:
            job_desc = job.xpath('./descendant::div[@class="job-snippet"]/ul/li/text()')
        except Exception as e:
            job_desc = ['Not available']
        if job_desc:
            job_desc = ",".join(job_desc)
        else:
            job_desc = 'Not available'
        return job_desc


def main():
    web_scraper = Scraper()
    web_scraper.scrape()


if __name__ == "__main__":
    main()
