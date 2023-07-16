from scraper import scrape


def main():
    scrape('software engineer', 'oregon',
           'https://www.glassdoor.com/Job/oregon-us-software-engineer-jobs-SRCH_IL.0,9_IS3163_KO10,27.htm')
    scrape('software engineer', 'oregon', scrape_option=1)
    scrape(
        glassdoor_start_url='https://www.glassdoor.com/Job/oregon-us-software-engineer-jobs-SRCH_IL.0,9_IS3163_KO10,27.htm',
        scrape_option=2)


if __name__ == "__main__":
    main()
