import json
from typing import List, Optional

from scrapy.http import Request, TextResponse


class BasePaapiResponse(TextResponse):
    pass


class GetBrowseNodesResponse(BasePaapiResponse):
    @property
    def browse_nodes(self) -> List[dict]:
        return self.json()["BrowseNodesResult"]["BrowseNodes"]


class GetItemsResponse(BasePaapiResponse):
    @property
    def items(self) -> List[dict]:
        return self.json()["ItemsResult"]["Items"]

    def follow_next_page(self) -> Optional[Request]:
        return None


class SearchItemsResponse(BasePaapiResponse):
    @property
    def items(self) -> List[dict]:
        return self.json()["SearchResult"]["Items"]

    def follow_next_page(self) -> Optional[Request]:
        data = json.loads(self.request.body)
        original_item_page = data.get("ItemPage", 1)
        original_item_count = data.get("ItemCount", 10)

        if original_item_page >= 10 or len(self.items) < original_item_count:
            return None  # no more next page

        data["ItemPage"] = original_item_page + 1
        return self.request.replace(data=data)
