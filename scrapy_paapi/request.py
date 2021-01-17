import json
from typing import List

from scrapy.http import Request
from scrapy_paapi.constant import (
    MARKETPLACE_TO_HOSTS,
    OPERATION_TO_PATHS,
    GET_ITEMS_RESOURCES,
)


class PaapiRequest(Request):
    def __init__(self, marketplace: str, partner_tag: str, operation: str, data: dict, **kwargs):
        host = MARKETPLACE_TO_HOSTS[marketplace]
        url = "https://" + host + OPERATION_TO_PATHS[operation]
        data["PartnerTag"] = partner_tag
        data["PartnerType"] = "Associates"
        data["Marketplace"] = marketplace
        data["Operation"] = operation

        super().__init__(
            url=url,
            method="POST",
            body=json.dumps(data),
            headers={
                "Accept": "application/json",
                "Accept-Language": "en-US",
                "Content-Encoding": "amz-1.0",
                "Content-Type": "application/json; charset=UTF-8",
                "Host": host,
                "X-Amz-Target": f"com.amazon.paapi5.v1.ProductAdvertisingAPIv1.{operation}",
            },
            **kwargs,
        )

    @classmethod
    def get_items(
        cls,
        marketplace: str,
        partner_tag: str,
        item_ids: List[str],
        resources: List[str] = None,
        **kwargs,
    ):
        resources = resources or GET_ITEMS_RESOURCES
        data = {"ItemIds": item_ids, "Resources": resources}

        return cls(
            marketplace=marketplace,
            partner_tag=partner_tag,
            operation="GetItems",
            data=data,
            **kwargs,
        )
