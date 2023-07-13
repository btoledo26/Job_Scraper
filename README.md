# Job_Scraper
## Info
A python module for scraping job listings from Indeed and Glassdoor. <br><br>
Inspired by: https://www.blog.datahut.co/post/scrape-indeed-using-selenium-and-beautifulsoup

## Usage
You can import a single function to either scrape both sites in one function call, or either site with individual function calls. 

```python
from scraper import scrape

scrape('software engineer', 'california')     # scrape Indeed and Glassdoor
scrape('software engineer', 'california', 1)  # only scrape Indeed
scrape('software engineer', 'california', 2)  # only scrape Glassdoor
```

The 'scrape' function creates a .csv file for each job board site containing the information of each job listing. This information includes the: URL, job title, company name, job location, salary, and job type for each listing as well as the job and location keywords used for the search. Duplicate listings are removed from the final output files.
