import os
from urllib.parse import urlparse

from scrapy.crawler import Crawler

from scrapy_paapi.constant import HOST_TO_REGIONS
from scrapy_paapi.signer import get_authorization_headers

AMZ_TARGET_PREFIX = b"com.amazon.paapi5.v1.ProductAdvertisingAPIv1."


class Aws4AuthMiddleware:
    def __init__(self, access_key: str, secret_key: str):
        self._access_key = access_key
        self._secret_key = secret_key

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        AMAZON_ACCESS_KEY = crawler.settings.get("AMAZON_ACCESS_KEY", os.environ.get("AMAZON_ACCESS_KEY"))
        AMAZON_SECRET_KEY = crawler.settings.get("AMAZON_SECRET_KEY", os.environ.get("AMAZON_SECRET_KEY"))

        return cls(access_key=AMAZON_ACCESS_KEY, secret_key=AMAZON_SECRET_KEY)

    def process_request(self, request, spider):
        o = urlparse(request.url)
        host = o.netloc
        region = HOST_TO_REGIONS.get(host)
        if not region:
            return  # proceed to next middleware

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
        amz_target = request.headers.get("X-Amz-Target")
        if (not amz_target) or (not amz_target.startswith(AMZ_TARGET_PREFIX)):
            return response

        operation = amz_target[len(AMZ_TARGET_PREFIX) :]
        if operation == b"GetItems":
            response.follow_next_page = lambda: None
            response.items = lambda: response.json()["ItemsResult"]["Items"]

        return response
