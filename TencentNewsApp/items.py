# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TencentnewsappItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    time = scrapy.Field()
    uinnick = scrapy.Field()
    source = scrapy.Field()
    type = scrapy.Field()
    comment_id = scrapy.Field()
    media_id = scrapy.Field()
    media_source = scrapy.Field()
    is_video = scrapy.Field()
    video_url = scrapy.Field()
    imgs_url = scrapy.Field()
    text = scrapy.Field()
    comment_count = scrapy.Field()
    comment_list = scrapy.Field()
