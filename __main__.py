from scraper import *


def main():
    # TODO: Add UI, get keywords from user input
    job_search_keyword = 'Software Engineer'
    location_search_keyword = 'Oregon'

    scrape(job_search_keyword, location_search_keyword)


if __name__ == "__main__":
    main()
