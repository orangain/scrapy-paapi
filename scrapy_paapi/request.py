import json
from typing import List, Optional

from scrapy.http import JsonRequest
from scrapy_paapi.constant import (
    MARKETPLACE_TO_HOSTS,
    OPERATION_TO_PATHS,
    GET_BROWSE_NODES_RESOURCES,
    GET_ITEMS_RESOURCES,
    SEARCH_ITEMS_RESOURCES,
)


class PaapiRequest(JsonRequest):
    def __init__(self, *args, **kwargs):
        body_passed = kwargs.get("body", None) is not None
        data = kwargs.get("data", None)

        if body_passed:
            data = json.loads(kwargs["body"])

        operation = data["Operation"]
        kwargs.setdefault("method", "POST")
        kwargs.setdefault("meta", {})["paapi_operation"] = operation
        kwargs.setdefault("headers", {}).update(
            {
                "Accept-Language": "en-US",
                "Content-Encoding": "amz-1.0",
                "X-Amz-Target": f"com.amazon.paapi5.v1.ProductAdvertisingAPIv1.{operation}",
            }
        )

        super().__init__(*args, **kwargs)

    @classmethod
    def of(cls, marketplace: str, partner_tag: str, operation: str, data: dict, **kwargs):
        host = MARKETPLACE_TO_HOSTS[marketplace]
        url = "https://" + host + OPERATION_TO_PATHS[operation]

        data["PartnerTag"] = partner_tag
        data["PartnerType"] = "Associates"
        data["Marketplace"] = marketplace
        data["Operation"] = operation

        return cls(url=url, data=data, **kwargs)

    @classmethod
    def get_browse_nodes(
        cls,
        marketplace: str,
        partner_tag: str,
        browse_node_ids: List[str],
        resources: List[str] = None,
        languages_of_preference: List[str] = None,
        **kwargs,
    ):
        """
        See: https://webservices.amazon.com/paapi5/documentation/getbrowsenodes.html
        """

        resources = resources or GET_BROWSE_NODES_RESOURCES
        data = {"BrowseNodeIds": browse_node_ids, "Resources": resources}
        if languages_of_preference is not None:
            data["LanguagesOfPreference"] = languages_of_preference

        return cls.of(
            marketplace=marketplace,
            partner_tag=partner_tag,
            operation="GetBrowseNodes",
            data=data,
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
        """
        See: https://webservices.amazon.com/paapi5/documentation/get-items.html
        """

        resources = resources or GET_ITEMS_RESOURCES
        data = {"ItemIds": item_ids, "Resources": resources}

        return cls.of(
            marketplace=marketplace,
            partner_tag=partner_tag,
            operation="GetItems",
            data=data,
            **kwargs,
        )

    @classmethod
    def search_items(
        cls,
        marketplace: str,
        partner_tag: str,
        browse_node_id: Optional[str] = None,
        item_page: Optional[int] = None,
        keywords: Optional[str] = None,
        languages_of_preference: List[str] = None,
        resources: List[str] = None,
        **kwargs,
    ):
        """
        See: https://webservices.amazon.com/paapi5/documentation/search-items.html
        """

        resources = resources or SEARCH_ITEMS_RESOURCES
        data = {"Resources": resources}
        if browse_node_id is not None:
            data["BrowseNodeId"] = browse_node_id
        if item_page is not None:
            data["ItemPage"] = item_page
        if keywords is not None:
            data["Keywords"] = keywords
        if languages_of_preference is not None:
            data["LanguagesOfPreference"] = languages_of_preference

        return cls.of(
            marketplace=marketplace,
            partner_tag=partner_tag,
            operation="SearchItems",
            data=data,
            **kwargs,
        )
