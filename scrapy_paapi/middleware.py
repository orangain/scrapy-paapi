import os
from urllib.parse import urlparse

from scrapy.crawler import Crawler

from scrapy_paapi.constant import HOST_TO_REGIONS
from scrapy_paapi.signer import get_authorization_headers
from scrapy_paapi.request import PaapiRequest
from scrapy_paapi.response import GetBrowseNodesResponse, GetItemsResponse, SearchItemsResponse


class PaapiMiddleware:
    def __init__(self, access_key: str, secret_key: str):
        self._access_key = access_key
        self._secret_key = secret_key

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        AMAZON_ACCESS_KEY = crawler.settings.get("AMAZON_ACCESS_KEY", os.environ.get("AMAZON_ACCESS_KEY"))
        AMAZON_SECRET_KEY = crawler.settings.get("AMAZON_SECRET_KEY", os.environ.get("AMAZON_SECRET_KEY"))

        return cls(access_key=AMAZON_ACCESS_KEY, secret_key=AMAZON_SECRET_KEY)

    def process_request(self, request, spider):
        if not isinstance(request, PaapiRequest):
            return  # proceed to next middleware

        o = urlparse(request.url)
        host = o.netloc
        region = HOST_TO_REGIONS[host]
        request.headers.setdefault("host", host)

        auth_headers = get_authorization_headers(
            self._access_key,
            self._secret_key,
            region,
            "ProductAdvertisingAPI",
            request.method,
            request.url,
            request.headers,
            request.body,
        )
        request.headers.update(auth_headers)  # Add auth headers

    def process_response(self, request, response, spider):
        if not isinstance(request, PaapiRequest):
            return response  # non-paapi response

        operation = request.meta["paapi_operation"]

        if operation == "GetBrowseNodes":
            return response.replace(cls=GetBrowseNodesResponse)
        elif operation == "GetItems":
            return response.replace(cls=GetItemsResponse)
        elif operation == "SearchItems":
            return response.replace(cls=SearchItemsResponse)

        return response
