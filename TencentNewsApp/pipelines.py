# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from .items import TencentnewsappItem
from pymongo import MongoClient
import logging


class TencentnewsappPipeline(object):

    def __init__(self):
        self.client = MongoClient()
        self.db = self.client['TencentNews']

    def process_item(self, item, spider):
        if isinstance(item, TencentnewsappItem):
            try:
                self.db[item['type']].insert_one(dict(item))
            except Exception:
                logging.debug('数据重复。重复id：{}'.format(item['_id']))
        return item

    def close_spider(self, spider):
        self.client.close()
