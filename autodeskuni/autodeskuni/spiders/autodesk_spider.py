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

        url_list = [f'https://www.autodesk.com/autodesk-university/au-online?page={i}' for i in range(num_pages+1)]

        for url in url_list[0]:
            yield Request(url=url, callback=self.parse_presentations_page)

    def parse_presentations_page(self, response):
        url_list = response.xpath('//div[@class="result grid"]/a/@href').extract()
        url_list = ['https://www.autodesk.com/' + remaining for remaining in url_list]

        for url in url_list[:2]:
            yield Request(url=url, callback=self.parse_description_page)

    def parse_description_page(self, response):

        city_year = response.xpath('//*[@id="class-wrapper"]/div/div[1]/div[2]/div[1]/nav/div/a[1]/text()').extract_first()
        title = response.xpath('//*[@id="class-wrapper"]/div/div[1]/div[2]/div[@class="au-content-banner__title"]/text()').extract_first() #remove \n's and strip
        description = response.xpath('//*[@id="class__main"]/div[1]/div/div[1]/div/text()').extract_first() #remove \n's and strip
        key_learnings = response.xpath('//*[@id="class__main"]/div[1]/div/div[2]/ul/li/text()').extract() #list
        tags_industry = response.xpath('//*[@id="class__main"]/div[5]/div[1]/table/tbody/tr[2]/td[2]/a/').extract() #XXXXXXX
        tags_topics = response.xpath('//*[@id="class__main"]/div[5]/div[1]/table/tbody/tr[3]/td[2]/a/text()').extract() #XXXXXXX
        recommend = response.xpath('//*[@id="dh-1613089211663"]/div/p/span[2]/div/span/text()').extract_first() #check on another url with non 0 recommendations

        item['title'] = title
        item['description'] = description
        item['city'] = city
        item['year'] = year
        item['key_learnings'] = key_learnings
        item['tags_product'] = tags_product
        item['tags_industry'] = tags_industry
        item['tags_topics'] = tags_topics
        item['recommend'] = recommend

        yield item