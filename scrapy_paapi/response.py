from scrapy.http import TextResponse


class BasePaapiResponse(TextResponse):
    pass


class GetBrowseNodesResponse(BasePaapiResponse):
    @property
    def browse_nodes(self):
        return self.json()["BrowseNodesResult"]["BrowseNodes"]


class GetItemsResponse(BasePaapiResponse):
    @property
    def items(self):
        return self.json()["ItemsResult"]["Items"]

    def follow_next_page(self):
        return None
