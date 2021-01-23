import json
from typing import List, Optional

from scrapy.http import Request, TextResponse


class BasePaapiResponse(TextResponse):
    pass


class PaapiErrorResponse(BasePaapiResponse):
    @property
    def error_type(self) -> str:
        return self.json()["__type"]

    @property
    def errors(self) -> List[dict]:
        return self.json()["Errors"]

    def __str__(self):
        error_messages = ", ".join((f"{error['Code']}: {error['Message']}" for error in self.errors))
        return f"<{self.status} {self.url} {error_messages}>"

    __repr__ = __str__


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
