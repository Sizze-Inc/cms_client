import aiohttp
from sizze_cms_service_client.api.collection import CmsClient


class ValuesClient(CmsClient):
    async def create(self, data: dict, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.base_url + "value/create/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def retrieve(self, **params):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "value/retrieve/",
                params=params
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def list(self, **params):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "value/list/",
                params=params
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def search(self, **params):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=self.base_url + "value/search/",
                    params=params
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def update(self, value_id: str, data: dict, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url=self.base_url + f"value/{value_id}/update/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def delete(self, value_id: str, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=self.base_url + f"value/{value_id}/delete/",
                params={"collection_position": collection_position}
            ) as response:
                if response.status == 204:
                    return None, response.status
                else:
                    response_body = await response.json()
                    return response_body, response.status

    async def copy(self, value_id: str, table_id: str, collection_position: int = 1):
        response_body, status_code = await self.retrieve(value_id=value_id, collection_position=collection_position)
        if status_code == 200:
            response_body, status_code = await self.create(
                {"values": response_body.get("values"), "table_id": table_id,
                 "collection_position": collection_position, "index": value_id}
            )
            return response_body, status_code
