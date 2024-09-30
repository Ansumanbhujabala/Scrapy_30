import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from Datascraper.spiders.final_scraper import CollegeSpider
# from Datascraper.spiders.final_scraper import json_file

# Configure logging
logging.basicConfig(
    filename='scrapy_process.log',  
    filemode='a',                  
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG            
)

def run():
    settings = get_project_settings()
    logging.info("Settings loaded: %s", settings)

    # logging.info("Started processing JSON file: %s", json_file)  

    process = CrawlerProcess(settings)
    logging.info("Crawler process created")

    process.crawl(CollegeSpider)
    logging.info("Crawl started")

    process.start()
    logging.info("Process finished")

    # logging.info("Finished processing JSON file: %s", json_file)  


if __name__ == "__main__":
    run()
