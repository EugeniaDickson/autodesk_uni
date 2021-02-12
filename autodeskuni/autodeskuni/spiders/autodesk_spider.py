from scrapy import Spider, Request
from autodeskuni.items import AutodeskuniItem
import re

class AutodeskSpider(Spider):
    name = 'autodesk_spider'
    allowed_urls = ['https://www.autodesk.com/']
    start_urls = ['https://www.autodesk.com/autodesk-university/au-online?facet_year[]=2011']

    def parse(self, response):
        years = response.xpath('//*[@id="form1"]/div[6]/div//label/text()').extract()
        years = sorted(years)
        
        url_list = [f"https://www.autodesk.com/autodesk-university/au-online?facet_year%5B0%5D={i}" for i in years]

        for url in url_list:
            yield Request(url=url, callback=self.parse_year)
    
    def parse_year(self, response):
        num_pages = response.xpath('//ul[@class="pager grid__item js-pager__items"]/li')[-1].xpath('./a/@href').extract_first()
        num_pages = int(num_pages.split("page=")[1])

        url_list = [response.url + f'&page={i}' for i in range(num_pages+1)]

        for url in url_list:
            yield Request(url=url, callback=self.parse_presentations_page)

    def parse_presentations_page(self, response):
        url_list = response.xpath('//div[@class="result grid"]/a/@href').extract()
        url_list = ['https://www.autodesk.com/' + remaining for remaining in url_list]

        for url in url_list:
            yield Request(url=url, callback=self.parse_description_page)

    def parse_description_page(self, response):
        ### EXTRACTING CITY ###
        city_year = response.xpath('//*[@id="class-wrapper"]/div/div[1]/div[2]/div[1]/nav/div/a[1]/text()').extract_first()
        year = int(re.findall('\d+', city_year)[0])
        city = re.findall('[A-Za-z- ]*', city_year)[0].strip()

        ### EXTRACTING TITLE ###
        title = response.xpath('//*[@id="class-wrapper"]/div/div[1]/div[2]/div[@class="au-content-banner__title"]/text()').extract_first().strip()
        title = re.sub("’", "'", title)

        ### EXTRACTING DESCRIPTION ###
        description = response.xpath('//*[@id="class__main"]/div[1]/div/div[1]/div/text()').extract_first().strip()
        description = re.sub("’", "'", description)

        ### EXTRACTING KEY LEARNINGS ###
        key_learnings = response.xpath('//*[@id="class__main"]/div[1]/div/div[2]/ul/li/text()').extract() #list
        key_learnings = ". ".join(key_learnings)
        key_learnings = re.sub("’", "'", key_learnings)

        ### EXTRACTING TAGS ###
        tags_all = response.xpath('//*[@id="class__main"]/div/div/table//text()').extract() #list

        #getting rid of extra spaces and empty strings
        tags_all = [tag.strip().lower() for tag in tags_all]
        tags_all = [tag for tag in tags_all if len(tag) != 0]

        #all tags come in one list so they need to be split
        #that's all possible groups but their combinations vary across all posts
        groups = ['product', 'industry', 'topics'] 

        indexes = []
        #if the name of the group appears in the list - fetch it's index
        #then separate lists by indexes
        [indexes.append(tags_all.index(tag)) for tag in tags_all if tag in groups]
        indexes.append(len(tags_all)+1) #appending end of the list index to get the last group in the list

        #function returns tuples of 1st and last indexes of each group
        def get_group_index(input_list):
            return list(zip(*[input_list[i:] for i in range(2)]))

        limits = get_group_index(indexes)

        tags_product = []
        tags_industry = []
        tags_topics = []

        #getting final lists of tags by group and converting them to strings delimited by pipe
        for lim in limits:
            temp = tags_all[lim[0]:lim[1]]
            name_temp = temp.pop(0)
            if name_temp == 'product':
                tags_product = '|'.join(temp)
            elif name_temp == 'industry':
                tags_industry = '|'.join(temp)
            elif name_temp == 'topics':
                tags_topics = '|'.join(temp)
        
        item = AutodeskuniItem()

        item['city'] = city
        item['year'] = year
        item['title'] = title
        item['description'] = description
        item['key_learnings'] = key_learnings
        item['tags_product'] = tags_product
        item['tags_industry'] = tags_industry
        item['tags_topics'] = tags_topics

        yield item