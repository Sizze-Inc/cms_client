import aiohttp
from sizze_cms_service_client.settings import base_url


class CmsClient:
    def __init__(self):
        self.__base_url = base_url
        self.__path = None
        self.__session = None

    @property
    def base_url(self):
        return self.__base_url

    @base_url.setter
    def base_url(self, value):
        self.__base_url = value

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, value):
        self.__path = value

    async def get_url(self):
        return self.base_url + self.path

    async def get_session(self):
        if not self.__session:
            self.__session = aiohttp.ClientSession()
        return self.__session

    async def send_request(self, method, data=None, **params):
        for param in params:
            if param is None:
                del param

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
        response_data = await response.json()
        status_code = response.status
        if status_code not in [200, 201, 204]:
            raise ServerError(response_data.get("message"))
        await session.close()
        return ServerResponse(status=status_code, data=response_data, _id=response_data.get("_id"))


class ServerResponse:
    def __init__(self, status: int, data: dict, _id=None):
        self.status = status
        self.data = data
        self.id = _id


class ServerError(Exception):
    pass
