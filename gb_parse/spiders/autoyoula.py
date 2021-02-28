import scrapy
from gb_parse.items import GbParseItem
import requests


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]
    _css_selectors = {
        "brands": "div.TransportMainFilters_brandsList__2tIkv "
        ".ColumnItemList_item__32nYI a.blackLink",
        "pagination": "div.Paginator_block__2XAPy a.Paginator_button__u1e7D",
        "car": "article.SerpSnippet_snippet__3O1t2 .SerpSnippet_titleWrapper__38bZM a.blackLink",
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
        description = {
            'year': response.css('div[data-target="advert-info-year"] a.blackLink::text').extract_first(),
            'mileage': response.css('div[data-target="advert-info-mileage"]::text').extract_first(),
            'body': response.css('div[data-target="advert-info-bodyType"] a.blackLink::text').extract_first(),
            'transmission': response.css('div[data-target="advert-info-transmission"]::text').extract_first(),
            'engine': response.css('div[data-target="advert-info-engineInfo"]::text').extract_first(),
            'wheel': response.css('div[data-target="advert-info-wheelType"]::text').extract_first(),
            'color': response.css('div[data-target="advert-info-color"]::text').extract_first(),
            'drive_type': response.css('div[data-target="advert-info-driveType"]::text').extract_first(),
            'power': response.css('div[data-target="advert-info-enginePower"]::text').extract_first(),
            'vin': response.css('div[data-target="advert-info-vinCode"]::text').extract_first(),
            'is_custom': response.css('div[data-target="advert-info-isCustom"]::text').extract_first(),
            'owners': response.css('div[data-target="advert-info-owners"]::text').extract_first(),
        }
        title = response.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first()
        img = response.css('button.PhotoGallery_thumbnailItem__UmhLO[style]').extract()
        img_urls = []
        for item in img:
            _, img_1 = item.split('(')
            img_url, _ = img_1.split(')')
            img_urls.append(img_url)
        author_url = response.css('a.SellerInfo_name__3Iz2N').attrib.get("href")

        yield GbParseItem(title=title, description=description, img_urls=img_urls, author_url=author_url)
