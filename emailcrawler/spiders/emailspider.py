# -*- coding: utf-8 -*-
import scrapy
import sys
import re
import scrapy_cloudflare_middleware
from extruct.w3cmicrodata import MicrodataExtractor
import json


data = {}

class EmailspiderSpider(scrapy.Spider):
    
    name = 'emailspider'
    allowed_domains = ['']
    start_urls = ['']
    # count = 0
    # file1 = open('websites.txt', 'r')
    # for line in file1:
    #     count += 1
    #     print("Line{}: {}".format(count, line.strip()))
    #     start_urls.append(line.strip())

    

    def start_requests(self):
        # headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        print("Using for loop")
        # Opening file
        file1 = open('websites.txt', 'r')

        count2 = 0
        for line in file1:
            count2 += 1
            print("Line{}: {}".format(count2, line.strip()))

        for url in self.start_urls:
            yield scrapy.Request("{}{}".format(url, line.strip()))

    def parse(self, response):
        url_to_follow = response.css(".r>a::attr(href)").extract()
        url_to_follow = [url.replace('/url?q=', '') for url in url_to_follow]
        for url in url_to_follow:
            yield scrapy.Request(
                url=url, callback=self.parse_email, dont_filter=True)

        next_pages_urls = response.css("#foot table a::attr(href)").extract()
        for page_num, url in enumerate(next_pages_urls):
            if(page_num < 11):
                next_page_url = response.urljoin(url)
                yield scrapy.Request(
                    url=next_page_url, callback=self.parse, dont_filter=True)
            else:
                break

    def parse_email(self, response):

        html_str = response.text
        emails = self.extract_email(html_str)
        phone_no = self.extract_phone_number(html_str)
        # logos = self.extract_logo(html_str)
        relative_src = response.css("img::attr(src)").extract()
        relative_href = response.css("img::attr(href)").extract()
        # relative_meta = response.css("meta::attr(content)").extract()
        relative_urls = relative_href + relative_src
        for relative_url in relative_urls:
            #static url
            relative_url = relative_url.split("svg")[0][2:-1]+".svg"
            relative_url = ''.join(relative_url.split("/thumb")).strip()

        # if(relative_url.find('logo') == True):
        relative_url = "http://"+relative_url
        print(relative_url)
        # if logo use meta tag
        # mde = MicrodataExtractor()
        # data = mde.extract(html_str)

        # with open("data.json", "w") as filee:
        #     filee.write('[')
        #     json.dump({
        #         "website": response.url,
        #         "emails": emails,
        #         "phone numbers": phone_no,
        #     }, filee) 

            # filee.write(']')

        yield{
            "website": response.url,
            "emails": emails,
            "phone numbers": phone_no,
            "logos": relative_url
        }

    def extract_email(self, html_as_str):
        return re.findall(r"[-.a-z]+@[^@\s\.]+\.[.a-z]{2,3}", html_as_str)
        # return re.findall(r'[\w\.-]+@[\w\.-]+', html_as_str)

    def extract_phone_number(self, html_as_str):
        #Generic International Phone Number
        return re.findall(r'\+\d{2}\s?0?\d{10}', html_as_str)