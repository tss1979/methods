import scrapy
from gb_parse.items import AutoyoulaItem
import requests
from ..loaders import AutoyoulaLoader

class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    _css_selectors = {
        "brands": ".TransportMainFilters_brandsList__2tIkv "
                  ".ColumnItemList_container__5gTrc "
                  "a.blackLink",
        "pagination": "a.Paginator_button__u1e7D",
        "car": ".SerpSnippet_titleWrapper__38bZM a.SerpSnippet_name__3F7Yu",
    }

    _car_xpaths = {
        "title": "//div[@data-target='advert']//div[@data-target='advert-title']/text()",
        "img_urls": "//div[@data-target='advert']//"
                    "figure[contains(@class, 'PhotoGallery_photo')]//img/@src",
        "characteristics": "//div[@data-target='advert']//"
                           "h3[contains(text(), 'Характеристики')]/../div/div",
        "price": "//head//title/text()",
        "author_url": "//script[contains(., 'window.transitState = decodeURIComponent')]/text()",
    }

    def _get_follow(self, response, select_str, callback, **kwargs):
        for a in response.css(select_str):
            link = a.attrib.get("href")
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response, self._css_selectors["brands"], self.brand_parse)

    def brand_parse(self, response, *args, **kwargs):

        yield from self._get_follow(response, self._css_selectors["pagination"], self.brand_parse)

        yield from self._get_follow(response, self._css_selectors["car"], self.car_parse)

    def car_parse(self, response):
        loader = AutoyoulaLoader(response=response)
        loader.add_value("url", response.url)
        for key, selector in self._car_xpaths.items():
            loader.add_xpath(key, selector)

        yield loader.load_item()
