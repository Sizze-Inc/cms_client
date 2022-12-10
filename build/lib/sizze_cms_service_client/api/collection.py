
class CmsClient:
    def __init__(self):
        self.base_url = None

    def get_base_url(self):
        return self.base_url

    def set_base_url(self, base_url):
        self.base_url = base_url
