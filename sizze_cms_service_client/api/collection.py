import aiohttp
from sizze_cms_service_client import settings


class CmsClient:
    def __init__(self):
        self.__path = None
        self.__session = None

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, value):
        self.__path = value

    @property
    def base_url(self):
        return settings.base_url

    async def get_url(self):
        return self.base_url + self.path

    async def get_session(self):
        if not self.__session or self.__session.closed:
            self.__session = aiohttp.ClientSession()
        return self.__session

    async def get_id_from_data(self, data):
        if isinstance(data, dict):
            _id = data.get("_id")
        else:
            _id = None
        return _id

    async def send_request(self, method, data=None, **params):
        for key, val in params.copy().items():
            if val is None:
                del params[key]

        session = await self.get_session()
        url = await self.get_url()
        match method:
            case "get":
                response = await session.get(url=url, params=params)
            case "post":
                response = await session.post(url=url, params=params, json=data)
            case "put":
                response = await session.put(url=url, params=params, json=data)
            case "delete":
                response = await session.delete(url=url, params=params)
            case _:
                raise ValueError("Method not found")
        if response.status == 204:
            response_data = dict()
        else:
            response_data = await response.json()
        await session.close()

        if response.status in [400, 422]:
            raise ServerError(response_data.get("message"))
        _id = await self.get_id_from_data(data=response_data)
        return ServerResponse(status=response.status, data=response_data, _id=_id)


class ServerResponse:
    def __init__(self, status: int, data: dict, _id=None):
        self.status = status
        self.data = data
        self.id = _id


class ServerError(Exception):
    pass
