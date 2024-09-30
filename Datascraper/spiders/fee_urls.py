# import scrapy

# class CollegeCoursesSpider(scrapy.Spider):
#     name = "college_courses"
# #     allowed_domains = ['collegedunia.com']
#     start_urls = [
#         'https://collegedunia.com/university/25581-ism-dhanbad-indian-institute-of-technology-iitism-dhanbad/courses-fees'
#     ]

#     def parse(self, response):
#         course_div = response.css('div.jsx-3337278764.college-content')
#         course_table = course_div.css('table.jsx-1226072102.table-new.table-striped.text-title.rounded-xl.mb-0')
#         print(course_table)
        
#         for link in course_table.css('a::attr(href)').getall():
#             print(link)
#             full_url = response.urljoin(link)
#             print(full_url)
#             yield {'course_url': full_url}