# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo

from gb_parse import settings
from scrapy.exceptions import DropItem
from pymongo import MongoClient


class GbParsePipeline(object):

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.autoyoula

    def process_item(self, item, spider):
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item


