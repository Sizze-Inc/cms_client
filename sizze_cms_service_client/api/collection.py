
class CmsClient:
    def __init__(self):
        self.base_url = None

    async def get_base_url(self):
        return self.base_url

    async def set_base_url(self, base_url):
        self.base_url = base_url
