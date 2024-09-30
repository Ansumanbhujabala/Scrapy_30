import scrapy
import os
import re
from pathlib import Path
from io import StringIO
from bs4 import BeautifulSoup
import pandas as pd
import json
from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from scrapy.crawler import CrawlerProcess
import os

# Get the directory of the current file and use it to build the full path
current_dir = os.path.dirname(os.path.abspath(__file__))



class CollegeSpider(scrapy.Spider):
    name = 'college_full_spider'

    sections = ["admission", "placement", "scholarship", "faculty", "hostel", "ranking","cutoff","general_info"]

    # saved_file_path = 'saved_file.txt'
    saved_file_path = os.path.join(current_dir, 'saved_file.txt')
    def get_file_paths(saved_file_path):
        with open(saved_file_path, 'r') as file:
            # Read all lines and strip out newlines/whitespace
            paths = [line.strip() for line in file.readlines() if line.strip()]
            return paths

    # Get the list of JSON file paths from saved_file.txt
    json_file_paths = get_file_paths(saved_file_path)

    json_file= json_file_paths[0]

    output_file = f'Output_{json_file}'


# Get the directory of the current file (final_scraper.py)
    current_dir = os.path.dirname(__file__)
    json_file_path = os.path.join(current_dir, 'jsonfolder', json_file)

# Check if the file exists
    if os.path.exists(json_file_path):
       with open(json_file_path, 'r') as file:
           data = json.load(file)
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>new")
        # print(data)
    else:
           print(f"File not found: {json_file_path}")


    # Extract URLs from the JSON data
    base_urls = [college['url'] for college in data]
    # print(base_urls)
    start_urls = []
    current_college_name = ""
    # Dictionary to store all scraped data
    all_data = {}

    for url in base_urls:
        start_urls.append(url)  # General info URL
        for section in sections[:-1]:  # Exclude 'general_info' for section-specific URLs
            start_urls.append(f"{url}/{section}")


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        section = response.url.split('/')[-1]

        # print(section)
        college_name = response.url.split('/')[4]

        if self.current_college_name == "" :
            self.current_college_name = college_name


        if self.current_college_name != college_name :
            self.save_to_json() 
            self.all_data={}
            self.current_college_name = college_name
        # if base_urls
        

        if college_name not in self.all_data:
            self.all_data[college_name] = {}
            self.current_college_name = college_name
        
        if section in self.sections[:-1]:  # Check if section is anything other than 'general_info'
            if section == "admission":
                self.all_data[college_name]['Admission'] = self.parse_admission(response, college_name)
            elif section == "placement":
                self.all_data[college_name]['Placement'] = self.parse_placement(response, college_name)
            elif section == "scholarship":
                self.all_data[college_name]['Scholarship'] = self.parse_scholarship(response, college_name)
            elif section == "faculty":
                self.all_data[college_name]['Faculty'] = self.parse_faculty(response, college_name)
            elif section == "hostel":
                self.all_data[college_name]['Hostel'] = self.parse_hostel(response, college_name)
            elif section == "ranking":
                self.all_data[college_name]['Ranking'] = self.parse_ranking(response, college_name)
            elif section == "cutoff":
                self.all_data[college_name]['Cutoff'] = self.parse_cutoff(response, college_name)


            # elif section == "reviews":
            #     self.all_data[college_name]['Reviews'] = self.parse_reviews(response, college_name)
        else:
            
            check_div = self.parse_college_page(response)
            
            (self.all_data[college_name])["college_name"] = check_div["college_name"]
            (self.all_data[college_name])['college_rating'] = check_div["college_rating"]
            (self.all_data[college_name])['review_number'] = check_div["review_number"]
            (self.all_data[college_name])['ratings'] = str(check_div["ratings"])
            (self.all_data[college_name])['header_data'] = str(check_div["header_data"])
            (self.all_data[college_name])['facilities'] = check_div["facilities"]
            (self.all_data[college_name])['contact_info'] = str(check_div["contact_info"])
            # (self.all_data[college_name])['overall_review'] = str(check_div["overall_review"])

            self.all_data[college_name]['General_Info'] = self.parse_general_info(response, college_name)
 

    def parse_general_info(self, response, college_name):
        content = []
        content_div = response.css('div.jsx-1612140807.about-section-reserve-height')
        content_html = content_div.get()
        soup = BeautifulSoup(content_html, 'html.parser')

        for section in soup.find_all(['h1', 'h2', 'h3','p','ul', 'li','table']):
            section_content = {
                'heading': None,
                'paragraphs': [],
                'tables': []
            }
            if section.name in ['h1', 'h2','h3']:
                section_content['heading'] = section.get_text(strip=True)
            elif section.name in ['p','ul','li']:
                section_content['paragraphs'].append(section.get_text(strip=True))
            elif section.name == 'table':
                df = pd.read_html(str(section))[0]
                transformed_table = self.transform_table(df)
                section_content['tables'].append(transformed_table)
            content.append(section_content)
        return content
    
    def parse_admission(self, response, college_name):
        content = []
        content_div = response.css('div.tab-data')
        content_html = content_div.get()
        soup = BeautifulSoup(content_html, 'html.parser')

        for section in soup.find_all(['h1', 'h2', 'h3','p','ul','li' 'table']):
            section_content = {
                'heading': None,
                'paragraphs': [],
                'tables': []
            }
            if section.name in ['h1', 'h2']:
                section_content['heading'] = section.get_text(strip=True)
            elif section.name in ['p','ul','li']:
                section_content['paragraphs'].append(section.get_text(strip=True))
            elif section.name == 'table':
                df = pd.read_html(str(section))[0]
                transformed_table = self.transform_table(df)
                section_content['tables'].append(transformed_table)
            content.append(section_content)
        return content

    def parse_placement(self, response, college_name):
        content = []
        content_div = response.css('div.article-full-reserve-height')
        content_html = content_div.get()
        soup = BeautifulSoup(content_html, 'html.parser')

        for section in soup.find_all(['h1', 'h2', 'h3','p','ul', 'table']):
            section_content = {
                'heading': None,
                'paragraphs': [],
                'tables': []
            }
            if section.name in ['h1', 'h2']:
                section_content['heading'] = section.get_text(strip=True)
            elif section.name in ['p','ul']:
                section_content['paragraphs'].append(section.get_text(strip=True))
            elif section.name == 'table':
                df = pd.read_html(str(section))[0]
                transformed_table = self.transform_table(df)
                section_content['tables'].append(transformed_table)
            content.append(section_content)
        return content

    def parse_cutoff(self, response, college_name):
        content = []
        content_div = response.css('div.jsx-422150313.rounded-16.p-6.bg-white.cutoff-reserve-height')
        content_html = content_div.get()
        soup = BeautifulSoup(content_html, 'html.parser')

        for section in soup.find_all(['h1', 'h2', 'h3','p','ul', 'table']):
            section_content = {
                'heading': None,
                'paragraphs': [],
                'tables': []
            }
            if section.name in ['h1', 'h2']:
                section_content['heading'] = section.get_text(strip=True)
            elif section.name in ['p','ul']:
                section_content['paragraphs'].append(section.get_text(strip=True))
            elif section.name == 'table':
                df = pd.read_html(str(section))[0]
                transformed_table = self.transform_table(df)
                section_content['tables'].append(transformed_table)
            content.append(section_content)
        return content

    def parse_scholarship(self, response, college_name):
        content = []

        sections = response.css('div#listing-article, div.cdcms_section1, div.cdcms_section2')

        for section in sections:
            section_content = {
                'heading': section.css('h2::text').get(),
                'paragraphs': section.css('p::text, ul li::text').getall(),
                'tables': []
            }

            tables = section.css('div.table-responsive table')
            for table in tables:
                table_html = table.get()
                df_list = pd.read_html(StringIO(table_html))
                for df in df_list:
                    transformed_table = self.transform_table(df)
                    section_content['tables'].append(transformed_table)

            content.append(section_content)
        
        return content

    def parse_faculty(self, response, college_name):
        content = []

        faculty_cards = response.xpath('//div[contains(@class, "faculty-card")]')
        
        section_content = {
            'heading': 'Faculty Information',
            'paragraphs': [],
            'tables': []
        }

        for card in faculty_cards:
            text = card.xpath('.//text()').getall()
            cleaned_text = ' - '.join([t.strip() for t in text if t.strip()])
            section_content['paragraphs'].append(cleaned_text)

        content.append(section_content)
        return content

    def parse_hostel(self, response, college_name):

        content = []
        content_div = response.css('div.jsx-2085888330.jsx-1484856324.hostel-fee.bg-white.rounded-16.p-6')
        content_html = content_div.get()
        soup = BeautifulSoup(content_html, 'html.parser')

        for section in soup.find_all(['h1', 'h2', 'h3','p','ul', 'table']):
            section_content = {
                'heading': None,
                'paragraphs': [],
                'tables': []
            }
            if section.name in ['h1', 'h2']:
                section_content['heading'] = section.get_text(strip=True)
            elif section.name in ['p','li','ul']:
                section_content['paragraphs'].append(section.get_text(strip=True))
            elif section.name == 'table':
                df = pd.read_html(str(section))[0]
                transformed_table = self.transform_table(df)
                section_content['tables'].append(transformed_table)
            content.append(section_content)
        return content

    def parse_ranking(self, response, college_name):
        content = []
        sections = response.css('div.jsx-3337278764.tab-data')
        content_html = sections.get()
        soup = BeautifulSoup(content_html, 'html.parser')

        for section in soup.find_all(['h1', 'h2', 'h3','p','ul', 'table']):
            section_content = {
                'heading': None,
                'paragraphs': [],
                'tables': []
            }
            if section.name in ['h1', 'h2']:
                section_content['heading'] = section.get_text(strip=True)
            elif section.name in ['p','ul']:
                section_content['paragraphs'].append(section.get_text(strip=True))
            elif section.name == 'table':
                df = pd.read_html(str(section))[0]
                transformed_table = self.transform_table(df)
                section_content['tables'].append(transformed_table)
            content.append(section_content)
        return content
    
    def parse_reviews(self, response, college_name):
        # content = []

        reviews = response.xpath('//div[@class="jsx-2083191045 clg-review"]//section[@class="jsx-3091098665 clg-review-card border-bottom py-4 border-gray-5"]')
        for review in reviews:
    # Extract the reviewer's name
            reviewer_name = review.xpath('.//div[@class="jsx-3091098665 d-flex justify-content-between"]/span/text()').get()

            # Extract the reviewer's rating
            reviewer_rating = review.xpath('.//div[@class="jsx-3091098665 rating d-flex align-items-center"]/span/text()').get()

            # Extract the branch of the reviewer
            reviewer_branch = review.xpath('.//div[@class="jsx-3091098665"]/span[@class="jsx-3091098665"]/text()').get()

            # Safely extract the review date
            review_date_list = review.xpath('.//div[@class="jsx-3091098665"]/span[@class="jsx-3091098665"]/text()').getall()
            review_date = review_date_list[1] if len(review_date_list) > 1 else None

            # Extract the Likes section
            likes = review.xpath('.//div[@id="likes-dislikes"]/li/text()').getall()

            # Extract the Dislikes section
            dislikes = review.xpath('.//div[@class="jsx-741742862 dislike-section ml-6 flex-1"]/li/text()').getall()

            # Extract the additional comments or any paragraphs under the specified div
            additional_comments = review.xpath('.//div[@class="jsx-2056580160 position-relative fs-16 font-weight-normal text-gray-10 mb-4"]/p/text()').getall()

        # Yield the extracted data
        overall_review = {
            'reviewer_name': reviewer_name,
            'reviewer_rating': reviewer_rating,
            'reviewer_branch': reviewer_branch,
            'review_date': review_date,
            'likes': likes,
            'dislikes': dislikes,
            'additional_comments': additional_comments,
        }
        return str(overall_review)

    def parse_college_page(self,response):
        # Scraping the h1 tag with the prefix "College name"
        college_name = response.xpath('//h1/text()').get()
        if college_name:
            college_name = (re.split(r'\s*:\s*', college_name)[0])


        header_info_div = response.xpath('//div[contains(@class, "jsx-3535035722 header_info ml-3")]')
        span_elements = header_info_div.xpath('.//span')

        # Extract and clean data
        university_data = []
        for span in span_elements:
            span_text = span.xpath('text()').get()
            if span_text is None:
                university_data.append("")
            else:
                university_data.append(span_text.strip())

        # scraping college review
        college_rating = response.css('div.jsx-3535035722.fs-30.font-weight-bold::text').get()
        # Scraping review ratings
        review_rating_div = response.xpath('//div[contains(@class, "jsx-3895350182 review-rating rounded-8 bg-lower-light py-4 px-6")]')
        review_a_text = review_rating_div.xpath('.//div[contains(@class, "jsx-3895350182 d-flex align-items-center mt-2")]/a/text()').get()


        reviews_data = {}

        # # Find all the divs with class 'jsx-3895350182 review-rating rounded-8 bg-lower-light py-4 px-6'
        review_categories = response.css('div.jsx-2813088169.review-rating-category.d-flex.gap-24')

        # Check if the selector found any matching elements
        if not review_categories:
            self.logger.error("No review categories found. Check your selectors.")

        # Loop through each review category
        for review_category in review_categories:
            
            # Loop through each div with class 'jsx-2813088169 rating-card d-flex flex-column align-items-center'
            rating_cards = review_category.css('div.jsx-2813088169.rating-card.d-flex.flex-column.align-items-center')

            # Check if the selector found any rating cards
            if not rating_cards:
                self.logger.warning(f"No rating cards found under review category. Check your selectors.")
            
            # Loop through each rating card to extract the text and number
            for rating_card in rating_cards:
                
                # Scrape text from 'div.jsx-2813088169.fs-14.font-weight-medium.text-primary-black.mt-1.rating-text'
                rating_text = rating_card.css('div.jsx-2813088169.fs-14.font-weight-medium.text-primary-black.mt-1.rating-text::text').get()

                # Scrape the number or text from 'span.jsx-2813088169'
                rating_number = rating_card.css('span.jsx-2813088169::text').get()

                reviews_data[rating_text] = rating_number
       
        facilities_data = [ ]

        facilities_div = response.css('div.jsx-332992735.video-section-clg.mt-4.d-flex')
        
        # Select all the divs with the img-container class inside the video section
        img_containers = facilities_div.css('div.jsx-332992735.img-container.d-flex.flex-column.align-items-center.justify-content-center.py-3.rounded-4.text-center')
        
        for container in img_containers:
            # Scrape the text inside each img-container div
            text_content = container.css('::text').getall()
            cleaned_text = [text.strip() for text in text_content if text.strip()]  # Clean whitespace
            facilities_data.extend(cleaned_text)
        # print(facilities_data)
        # Scraping location section (id="location")
        location_section = response.xpath('//section[@id="location"]')
        location_h2 = location_section.xpath('.//h2/text()').get()
        location_p = location_section.xpath('.//p/text()').get()

        # Scraping text (including from span and br tags) from div class `jsx-1623489515 d-flex align-items-center`
        align_items_divs = response.xpath('//div[contains(@class, "jsx-1623489515 d-flex align-items-center")]')
        align_items_texts = []

        for div in align_items_divs:
            span_texts = div.xpath('.//span/text()').getall()
            br_texts = div.xpath('.//text()[normalize-space()]').getall()
            
            # Join all the `br_texts` into a single string for each `div`
            combined_text = ' '.join([text.strip() for text in br_texts if text.strip()])

            if combined_text:  # Only append if there's non-empty text
                align_items_texts.append(combined_text)
            # print(combined_text)
        output_data_2= {
            "address": align_items_texts[0],
            "sms_text": align_items_texts[1][-12:],
            "call_details": align_items_texts[2][-12:],
            "web_link": align_items_texts[3].split('Website Link:')[1].strip()

        }

    
        return {
            'college_name': college_name ,
            'college_rating':college_rating,
            'header_data': university_data,
            
            'review_number': review_a_text.strip() if review_a_text else "No a tag text found",
            'ratings': reviews_data,            
            'facilities':facilities_data, 
            'location_h2': location_h2.strip() if location_h2 else "No location h2 found",
            'contact_info' : output_data_2,
        }

    def transform_table(self, df):
        # Clean the DataFrame: remove empty rows/columns
        df = df.dropna(how='all').dropna(axis=1, how='all')

        # If the DataFrame has MultiIndex columns, flatten them
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [' '.join(map(str, col)).strip() for col in df.columns]  # Flatten to a string
        else:
            df.columns = df.columns.map(lambda x: str(x).strip())  # Ensure columns are strings

        # Strip whitespace from the data, only for string types
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        return df

    def save_to_json(self):
        # Initialize an empty dictionary to hold all the data
        combined_data = {}
        output_file = self.output_file

        for college_name, sections in self.all_data.items():
            # Prepare data for JSON serialization
            serializable_data = {}
            for section_name, content in sections.items():
                serializable_content = []
                if not isinstance(content, str):
                    for item in content:
                        # print(item)
                        # Check if the item is a dictionary or some other object with a `copy()` method
                        if isinstance(item, dict):
                            serializable_item = item.copy()

                            # Convert DataFrames to lists of lists
                            if 'tables' in item:
                                serializable_item['tables'] = [df.to_dict(orient='records') for df in item['tables']]
                        else:
                            # If item is a string or any other type, directly assign it
                            serializable_item = item

                        serializable_content.append(serializable_item)
                    serializable_data[section_name] = serializable_content
                    
                    
                else:
                    serializable_data[section_name] = content
            # Add the serializable_data for this college to the combined data
            combined_data[college_name] = serializable_data
            # print(combined_data)
        # Save all college data to one JSON file
        if os.path.isfile(output_file):
            print("Found")
        else:
            print("Not Found")    

        with open(output_file, 'a', encoding='utf-8') as json_file:
            file_exists = os.path.isfile(output_file)
            file_empty = file_exists and os.path.getsize(output_file) == 0
            if file_empty:
                json_file.write('[\n')
            json.dump(combined_data, json_file, ensure_ascii=False, indent=4)
            json_file.write(',\n')



    def closed(self, reason):
        output_file=self.output_file
        print("succesfull")
        if self.all_data:
            self.save_to_json()
        with open(output_file, 'a', encoding='utf-8') as json_file:
            json_file.seek(0, 2)  
            file_size = json_file.tell()
            json_file.seek(file_size - 2)
            json_file.truncate()
            json_file.write('\n]')


        # This method is called when the spider is closed
        # self.save_to_excel()
        # self.save_to_json()
        # process = CrawlerProcess()
        # process.crawl(CollegeSpider)
        # process.start()


