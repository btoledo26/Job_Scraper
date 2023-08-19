# Job_Scraper
A python module for scraping job listings from Indeed and Glassdoor. 

> **Warning**<br>
> Currently broken due to the sites implementing stronger anti-automation countermeasures.

## Info
This project was initially started as a personal tool, and was also meant to serve as a way to learn web scraping with Python. At the start I attempted to just use Selenium for the web driver and data parsing, but found that it was much simpler to use Beautiful Soup and lxml as well to parse the site data. Also, while it may seem strange to have sleep calls in the scraping loops, this is done in an attempt to not get blocked from accessing these job board sites.
<br><br>
Inspired by: https://www.blog.datahut.co/post/scrape-indeed-using-selenium-and-beautifulsoup

## Usage
You can import a single function to either scrape both sites in one function call, or either site with individual function calls. Due to how Glassdoor uses unique values in the URL based on the searched location, the starting URL for Glassdoor must be provided to the function. 

```python
from scraper import scrape

# scrape Indeed and Glassdoor
scrape('software engineer', 'oregon', 'https://www.glassdoor.com/Job/oregon-us-software-engineer-jobs-SRCH_IL.0,9_IS3163_KO10,27.htm')
# only scrape Indeed
scrape('software engineer', 'oregon', scrape_option=1)
# only scrape Glassdoor
scrape(glassdoor_start_url='https://www.glassdoor.com/Job/oregon-us-software-engineer-jobs-SRCH_IL.0,9_IS3163_KO10,27.htm', scrape_option=2)
```

The 'scrape' function creates a .csv file for each job board site containing the information of each job listing. This information includes the: URL, job title, company name, job location, salary, and job type for each listing as well as the job and location keywords used for the search. Duplicate listings are removed from the final output files.

> **Note**<br>
> To gather the starting URL for Glassdoor just go to their site, search based on your desired job title and location, and copy the URL for the resulting page as shown below.

![Untitled](https://github.com/btoledo26/Job_Scraper/assets/59942879/0e909339-118d-4dc2-b4cc-2e6d1fbe0a76)
