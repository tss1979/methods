import time
import json
from pathlib import Path
import requests


class Parse5Ka:
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10.16; rv:85.0) "
        "Gecko/20100101 Firefox/85.0",
    }

    def __init__(self, start_url: str, category_url: str, cat_path: Path):
        self.start_url = start_url
        self.cat_url = category_url
        self.cat_path = cat_path

    def _get_response(self, url):
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def run(self):
        for item in self._parse(self.start_url, self.cat_url):
            category_path = self.cat_path.joinpath(f"{item[0]['parent_group_code']}.json")
            data_result = {'name': item[0]['parent_group_name'], 'code': item[0]['parent_group_code'], 'products': item[1]}
            self._save(data_result, category_path)

    def _parse(self, start_url, url_of_cat):
        result = []
        response_cat = self._get_response(url_of_cat)
        categories = response_cat.json()
        for category in categories:
            result_prod = []
            code = category['parent_group_code']
            next_url = start_url
            while next_url:
                if next_url == start_url:
                    response = self._get_response(start_url + f'?categories={code}')
                    print(start_url + f'?categories={code}')
                    data = response.json()
                    next_url = data['next']
                else:
                    response = self._get_response(next_url)
                    data = response.json()
                    next_url = data['next']
                result_prod.append(data['results'])
            result.append([category, result_prod])
        return result

    @staticmethod
    def _save(product, file_path):
        j_data = json.dumps(product, ensure_ascii=False)
        file_path.write_text(j_data, encoding="UTF-8")


if __name__ == "__main__":
    url = "https://5ka.ru/api/v2/special_offers/"
    cat_url = "https://5ka.ru/api/v2/categories/"
    save_path = Path(__file__).parent.joinpath("categories_products")
    if not save_path.exists():
        save_path.mkdir()

    parser = Parse5Ka(url, cat_url, save_path)
    parser.run()


