
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


class CmsResult:
    def __init__(self, result: bool, error: str = None):
        self.result = result
        self.error = error


class RetrieveResult(CmsResult):
    def __init__(self, result=True, error=None, _id: str = None, data: dict = None):
        super().__init__(result=result, error=error)
        self.id = _id
        self.data = data

    def __str__(self):
        return self.data

    def __repr__(self):
        return self.data


class ListResult(CmsResult):
    def __init__(self, result=True, error=None, _ids: list = None, data: list = None):
        super().__init__(result=result, error=error)
        self.ids = _ids
        self.data = data

    def __str__(self):
        return self.ids

    def __repr__(self):
        return self.ids


class CreateUpdateResult(CmsResult):
    def __init__(self, result=True, error=None, _id: str = None):
        super().__init__(result=result, error=error)
        self.id = _id

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id


class DeleteResult(CmsResult):
    def __init__(self, result=True, error=None):
        super().__init__(result=result, error=error)
