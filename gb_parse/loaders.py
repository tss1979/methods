from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join

import re
from gb_parse.items import AutoyoulaItem
from gb_parse.items import HhItem
import urllib.parse as u


def get_characteristics(item) -> dict:
    selector = Selector(text=item)
    return {
        "name": selector.xpath(
            '//div[contains(@class, "AdvertSpecs_label")]/text()'
        ).extract_first(),
        "value": selector.xpath(
            '//div[contains(@class, "AdvertSpecs_data")]//text()'
        ).extract_first(),
    }


def get_price(item):
    re_pattern = re.compile(r"цена ([\s\d]+) руб")
    result = re.findall(re_pattern, item)
    return float(str(result[0]).replace(' ', '')) if result else None


def get_author_id(item) -> str:
    marker = "window.transitState = decodeURIComponent"
    if marker in item:
        re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
        result = re.findall(re_pattern, item)
        return f"https://youla.ru/user/{result[0]}" if result else None


class AutoyoulaLoader(ItemLoader):
    default_item_class = AutoyoulaItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_in = MapCompose(get_price)
    price_out = TakeFirst()
    characteristics_in = MapCompose(get_characteristics)
    author_url_in = MapCompose(get_author_id)


def get_hh_salary(item):
    item = item.replace('\xa000', '')
    item = item.replace('\xa09000', '')
    return item


class HhLoader(ItemLoader):
    default_item_class = HhItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_in = MapCompose(get_hh_salary)
    salary_out = Join()
    author_url_out = TakeFirst()
    description_out = Join()
