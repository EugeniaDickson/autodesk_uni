from scrapy import Spider, Request
from autodeskuni.items import AutodeskuniItem
import re

class AutodeskSpider(Spider):
    name = 'autodesk_spider'
    allowed_urls = ['https://www.autodesk.com/']
    start_urls = ['https://www.autodesk.com/autodesk-university/au-online?page=0']

    def parse(self, response):
        num_pages = response.xpath('//ul[@class="pager grid__item js-pager__items"]/li')[-1].xpath('./a/@href').extract_first()
        num_pages = int(re.search('\d+', num_pages)[0])

        url_list = [f'https://www.autodesk.com/autodesk-university/au-online?page={i}' for i in range(num+1)]

        for url in url_list[0]:
            yield Request(url=url, callback=self.parse_presentations_page)

    def parse_presentations_page(self, response):
        url_list = response.xpath('//div[@class="result grid"]/a/@href').extract()
        url_list = ['https://www.autodesk.com/' + remaining for remaining in url_list]

        for url in url_list[:2]:
            yield Request(url=url, callback=self.parse_description_page)

    def parse_description_page(self, response):


        item['title'] = title
        item['description'] = description
        item['city'] = city
        item['year'] = year
        item['key_learnings'] = key_learnings
        item['tags_industry'] = tags_industry
        item['tags_topics'] = tags_topics
        item['recommend'] = recommend

        yield item