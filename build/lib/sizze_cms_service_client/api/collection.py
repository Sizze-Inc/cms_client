
class CmsClient:
    def __init__(self, base_url=None, collection_position=None):
        self.base_url = base_url
        self.split_char = "$"
        self.collection_position = collection_position

    def get_base_url(self):
        return self.base_url

    def set_base_url(self, base_url):
        self.base_url = base_url

    def get_collection_position(self):
        return self.collection_position

    def set_collection_position(self, collection_position):
        self.collection_position = collection_position
