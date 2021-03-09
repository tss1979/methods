import scrapy

from ..loaders import HhLoader


class HhSpider(scrapy.Spider):
    name = "hh"
    allowed_domains = ["hh.ru"]
    start_urls = ["https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113/"]

    _xpaths_selectors = {
        "vacancy": "//div[@class='vacancy-serp-item__info']//a[@data-qa='vacancy-serp__vacancy-title']/@href",
        "pagination": "//div[@data-qa='pager-block']//a[@data-qa='pager-page']/@href",
    }

    _vac_xpaths = {
        "title": "//div[@class='vacancy-title']/h1[@data-qa='vacancy-title']/span/text()",
        "salary": "//div[@class='vacancy-title']//p[@class='vacancy-salary']/span[@data-qa='bloko-header-2']/text()",
        "description": "//div[@data-qa='vacancy-description']/p/text()",
        "key_skills": "//div[@data-qa='bloko-tag bloko-tag_inline skills-element']//"
                      "span[@data-qa='bloko-tag__text']/text()",
        "author_url": "//div[@class='vacancy-company__details']//a[@data-qa='vacancy-company-name']/@href",
    }

    def _get_follow(self, response, select_str, callback, **kwargs):
        for link in response.xpath(select_str).extract():
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response, self._xpaths_selectors['pagination'], self.parse_page)

    def parse_page(self, response, *args, **kwargs):
        yield from self._get_follow(response, self._xpaths_selectors['vacancy'], self.parse_vac)


    def parse_vac(self, response):
        loader = HhLoader(response=response)
        loader.add_value("url", response.url)
        for key, selector in self._vac_xpaths.items():
            loader.add_xpath(key, selector)
        yield loader.load_item()
