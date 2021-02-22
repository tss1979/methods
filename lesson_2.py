
import requests
from urllib.parse import urljoin
import bs4
import pymongo
import datetime
import time


class MagnitParse:

    def __init__(self, start_url, db_client):
        self.start_url = start_url
        self.db = db_client["gb_data_mining_16_02_2021"]

    @staticmethod
    def _get_response(url):
        while True:
            response = requests.get(url)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def _get_soup(self, url):
        while True:
            response = self._get_response(url)
            if response.status_code == 200:
                soup = bs4.BeautifulSoup(response.text, "lxml")
                return soup
            time.sleep(0.5)

    @staticmethod
    def _parce_price(a):
        if a:
            first_part = a.find("span", attrs={"class": "label__price-integer"}).text
            second_part = a.find("span", attrs={"class": "label__price-decimal"}).text
            return float(first_part + '.' + second_part)
        else:
            return None

    @staticmethod
    def _parce_date(a, y):
        p = a.find("div", attrs={"class": "card-sale__date"}).find_all("p")
        month = {'января': 1,
                 'февраля': 2,
                 'марта': 3,
                 'апреля': 4,
                 'мая': 5,
                 'июня': 6,
                 'июля': 7,
                 'августа': 8,
                 'сентября': 9,
                 'октября': 10,
                 'ноября': 11,
                 'декабря': 12,
                 }
        string_from, date_from, month_from = p[0].text.split(' ')
        string_till, date_till, month_till = p[1].text.split(' ')
        if y == 1:
            date_from = datetime.date(datetime.datetime.now().year, month[month_from], int(date_from))
            return str(date_from)
        elif y == 2:
            date_till = datetime.date(datetime.datetime.now().year, month[month_till], int(date_till))
            return str(date_till)
        else:
            raise ValueError

    def _template(self):
        return {
            "url": lambda a: urljoin(self.start_url, a.attrs.get("href")),
            "promo_name": lambda a: a.find("div", attrs={"class": "card-sale__header"}).text,
            "title": lambda a: a.find("div", attrs={"class": "card-sale__title"}).text,
            "old_price": lambda a: self._parce_price(a.parent.find("div", attrs={"class": "label__price_old"})),
            "new_price": lambda a: self._parce_price(a.parent.find("div", attrs={"class": "label__price_new"})),
            "image_url": lambda a: urljoin(self.start_url, a.find("img").attrs.get("data-src")),
            "date_from": lambda a: self._parce_date(a.parent, 1),
            "date_to": lambda a: self._parce_date(a.parent, 2),
        }

    def run(self):
        soup = self._get_soup(self.start_url)
        catalog = soup.find("div", attrs={"class": "сatalogue__main"})
        for product_a in catalog.find_all("a", recursive=False):
            product_data = self._parse(product_a)
            self.save(product_data)

    def _parse(self, product_a: bs4.Tag) -> dict:
        product_data = {}
        for key, funk in self._template().items():
            try:
                product_data[key] = funk(product_a)
            except AttributeError:
                pass

        return product_data

    def save(self, data: dict):
        collection = self.db["magnit"]
        collection.insert_one(data)


if __name__ == "__main__":
    url = "https://magnit.ru/promo/"
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    parser = MagnitParse(url, db_client)
    parser.run()


