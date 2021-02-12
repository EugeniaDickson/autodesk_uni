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

        ### EXTRACTING CITY ###
        city_year = response.xpath('//*[@id="class-wrapper"]/div/div[1]/div[2]/div[1]/nav/div/a[1]/text()').extract_first()
        city = city_year.split(' ')[0]
        year = city_year.split(' ')[1]

        ### EXTRACTING TITLE ###
        title = response.xpath('//*[@id="class-wrapper"]/div/div[1]/div[2]/div[@class="au-content-banner__title"]/text()').extract_first().strip()

        ### EXTRACTING DESCRIPTION ###
        description = response.xpath('//*[@id="class__main"]/div[1]/div/div[1]/div/text()').extract_first().strip()

        ### EXTRACTING KEY LEARNINGS ###
        key_learnings = response.xpath('//*[@id="class__main"]/div[1]/div/div[2]/ul/li/text()').extract() #list

        ### EXTRACTING TAGS ###
        tags_all = response.xpath('//*[@id="class__main"]/div[5]/div[1]/table//text()').extract().strip()

        #getting rid of extra spaces and empty strings
        tags_all = [tag.strip().lower() for tag in tags_all]
        tags_all = [tag for tag in tags_all if len(tag) != 0]

        #splitting tags by groups
        groups = ['product', 'industry', 'topics']

        indexes= []
        [indexes.append(tags_all.index(tag)) for tag in tags_all if tag in groups]

        tags_product = tags_all[indexes[0]+1:indexes[1]]
        tags_industry = tags_all[indexes[1]+1:indexes[2]]
        tags_topics = tags_all[indexes[2]+1:]

        ### EXTRACTING NUMBER OF PEOPLE WHO LIKED THE PRESENTATION ###
        recommend = response.xpath('//div[@class="au-content-banner__bottom container container--dynamic"]//text()').extract() #unable to get any rec/comment data from the entire div

        ### EXTRACTING NUMBER OF COMMENTS ###
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