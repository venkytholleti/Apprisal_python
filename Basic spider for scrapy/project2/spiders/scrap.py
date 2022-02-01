from urllib import response
from urllib.parse import urlparse
import scrapy


class QuotesSpider(scrapy.Spider):
    name = 'scrap'
    def start_requests(self):
                
        start_urls = [
                'https://www.codecademy.com/learn/learn-intermediate-python-3',
            ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
            yield {
                
                'Why Learn Intermediate Python' :response.css('p.p__1qg33Igem5pAgn4kPMirjw::text')[0].get(), 
                'takeawayskills' :response.css('p.p__1qg33Igem5pAgn4kPMirjw::text')[1:3].getall(),
                'points' :response.css('ul.ul__11icM1EC_0uPj3OY0Skp4r li::text').getall(),       
                'Duration' : response.css('span.gamut-1sk71u6-Text.e8i0p5k0::text')[3].get()        

                

            }