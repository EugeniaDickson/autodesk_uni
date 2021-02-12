# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class AutodeskuniItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    city = scrapy.Field()
    year = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    key_learnings = scrapy.Field()
    tags_product = scrapy.Field()
    tags_industry = scrapy.Field()
    tags_topics = scrapy.Field()
