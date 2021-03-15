import json
from copy import deepcopy
import datetime as dt
from urllib.parse import urlencode
import scrapy
from ..items import InstaTag, InstaPost, InstaUser, InstaFollower, InstaFollowed


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com"]
    start_urls = ["https://www.instagram.com/"]
    _login_url = "https://www.instagram.com/accounts/login/ajax/"
    _tags_path = "/explore/tags/"
    api_url = "/graphql/query/"

    def __init__(self, login, password, tags, users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.tags = tags
        self.users = users

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self._login_url,
                method="POST",
                callback=self.parse,
                formdata={"username": self.login, "enc_password": self.password, },
                headers={"X-CSRFToken": js_data["config"]["csrf_token"]},
            )
        except AttributeError as e:
            print(e)
            if response.json()["authenticated"]:
                # for tag in self.tags:
                #     yield response.follow(f"{self._tags_path}{tag}/", callback=self.tag_page_parse)
                for user_name in self.users:
                    yield response.follow(f"/{user_name}/", callback=self.user_page_parse)

    def tag_page_parse(self, response):
        js_data = self.js_data_extract(response)
        insta_tag = InstTag(js_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"])
        yield insta_tag.get_tag_item()
        yield from insta_tag.get_post_items()
        yield response.follow(
            f"{self.api_url}?{urlencode(insta_tag.paginate_params())}",
            callback=self._api_tag_parse,
        )

    def user_page_parse(self, response):
        js_data = self.js_data_extract(response)
        insta_user = InstUser(js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"])
        yield insta_user.get_user_item()
        yield response.follow(
            f"{self.api_url}?{urlencode(insta_user.get_followers_vars())}",
            callback=self._api_follow_parse,
            cb_kwargs={"insta_user": insta_user},
        )
        yield response.follow(
            f"{self.api_url}?{urlencode(insta_user.get_followed_vars())}",
            callback=self._api_follow_parse,
            cb_kwargs={"insta_user": insta_user},
        )

    def _api_follow_parse(self, response, **cb_kwargs):
        data = response.json()
        marker = data['data']['user'].keys()
        fol = []
        if 'edge_follow' in marker:
            edges = data['data']['user']['edge_follow']['edges']
            for edge in edges:
                fol.append(edge['node']['id'])
            yield cb_kwargs['insta_user'].get_follower_item(fol)
        elif 'edge_followed_by' in marker:
            edges = data['data']['user']['edge_followed_by']['edges']
            for edge in edges:
                fol.append(edge['node']['id'])
            yield cb_kwargs['insta_user'].get_followed_item(fol)
        else:
            raise TypeError


    def _api_tag_parse(self, response):
        data = response.json()
        insta_tag = InstTag(data["data"]["hashtag"])
        yield from insta_tag.get_post_items()
        yield response.follow(
            f"{self.api_url}?{urlencode(insta_tag.paginate_params())}",
            callback=self._api_tag_parse,
        )

    def js_data_extract(self, response):
        script = response.xpath(
            "//script[contains(text(), 'window._sharedData = ')]/text()"
        ).extract_first()
        return json.loads(script.replace("window._sharedData = ", "")[:-1])


class InstTag:
    query_hash = "9b498c08113f1e09617a1703c22b2f32"

    def __init__(self, hashtag: dict):
        self.variables = {
            "tag_name": hashtag["name"],
            "first": 100,
            "after": hashtag["edge_hashtag_to_media"]["page_info"]["end_cursor"],
        }
        self.hashtag = hashtag

    def get_tag_item(self):
        item = InstaTag()
        item["date_parse"] = dt.datetime.utcnow()
        data = {}
        for key, value in self.hashtag.items():
            if not (isinstance(value, dict) or isinstance(value, list)):
                data[key] = value
        item["data"] = data
        return item

    def paginate_params(self):
        url_query = {"query_hash": self.query_hash, "variables": json.dumps(self.variables)}
        return url_query

    def get_post_items(self):
        for edge in self.hashtag["edge_hashtag_to_media"]["edges"]:
            yield InstaPost(date_parse=dt.datetime.utcnow(), data=edge["node"])


class InstUser:
    def __init__(self, user):
        self.user = user
        self.user_followers = InstaFollowers(user["id"])

    def get_user_item(self):
        data = {}
        for key, value in self.user.items():
            if not (isinstance(value, dict) or isinstance(value, list)):
                data[key] = value
        return InstaUser(date_parse=dt.datetime.utcnow(), data=data)

    def get_followed_vars(self):
        return self.user_followers.get_variables("followed")

    def get_followers_vars(self):
        return self.user_followers.get_variables("followers")

    def get_follower_item(self, data):
        return InstaFollower(date_parse=dt.datetime.utcnow(), data=data, user_id=self.user['id'])

    def get_followed_item(self, data):
        return InstaFollowed(date_parse=dt.datetime.utcnow(), data=data, user_id=self.user['id'])


class InstaFollowers:
    query_hashs = {
        "followers": {"query": "3dec7e2c57367ef3da3d987d89f9dbc8", "next": None},
        "followed": {"query": "5aefa9893005572d237da5068082d8d5", "next": None},
    }

    def __init__(self, user_id):
        self.user_id = user_id
        self.variables = {"id": user_id, "include_reel": True, "fetch_mutual": True, "first": 24}

    def get_variables(self, key):
        variables = deepcopy(self.variables)
        if self.query_hashs[key]["next"]:
            variables["after"] = self.query_hashs[key]["next"]

        url_query = {
            "query_hash": self.query_hashs[key]["query"],
            "variables": json.dumps(self.variables),
        }
        return url_query




