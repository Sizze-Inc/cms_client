
class CmsClient:
    def __init__(self, base_url=None):
        self.base_url = base_url

    def get_base_url(self):
        return self.base_url

    def set_base_url(self, base_url):
        self.base_url = base_url
