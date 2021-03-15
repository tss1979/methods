# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AutoyoulaItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    characteristics = scrapy.Field()
    img_urls = scrapy.Field()
    author_url = scrapy.Field()


class HhItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    key_skills = scrapy.Field()
    author_url = scrapy.Field()
    description = scrapy.Field()


class Insta(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    photos = scrapy.Field()


class InstaTag(Insta):
    pass


class InstaPost(Insta):
    pass


class InstaUser(Insta):
    pass


class InstaFollower(Insta):
    user_id = scrapy.Field()
    pass



class InstaFollowed(Insta):
    user_id = scrapy.Field()
    pass
