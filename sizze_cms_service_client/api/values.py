import aiohttp
from sizze_cms_service_client.api.collection import CmsClient, CreateUpdateResult, RetrieveResult, ListResult, \
    DeleteResult


class ValuesClient(CmsClient):
    async def create(self, data: dict, collection_position: int = 1) -> CreateUpdateResult:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.base_url + "value/create/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                if response.status == 201:
                    _id = response_body.get("_id")
                    value_response = CreateUpdateResult(_id=_id)
                else:
                    value_response = CreateUpdateResult(result=False, error=response_body.get("message"))
                return value_response

    async def retrieve(self, **params) -> RetrieveResult:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "value/retrieve/",
                params=params
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    _id = response_body.get("_id")
                    value_response = RetrieveResult(_id=_id, data=response_body)
                else:
                    value_response = RetrieveResult(result=False, error=response_body.get("message"))
                return value_response

    async def list(self, **params) -> ListResult:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "value/list/",
                params=params
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    _ids = [field.get("_id") for field in response_body]
                    value_response = ListResult(data=response_body, _ids=_ids)
                else:
                    value_response = ListResult(result=False, error=response_body.get("message"))
                return value_response

    async def search(self, **params) -> ListResult:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=self.base_url + "value/search/",
                    params=params
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    _ids = [field.get("_id") for field in response_body]
                    value_response = ListResult(data=response_body, _ids=_ids)
                else:
                    value_response = ListResult(result=False, error=response_body.get("message"))
                return value_response

    async def update(self, value_id: str, data: dict, collection_position: int = 1) -> CreateUpdateResult:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url=self.base_url + f"value/{value_id}/update/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    _id = response_body.get("_id")
                    value_response = CreateUpdateResult(_id=_id)
                else:
                    value_response = CreateUpdateResult(result=False, error=response_body.get("message"))
                return value_response

    async def delete(self, value_id: str, collection_position: int = 1) -> DeleteResult:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=self.base_url + f"value/{value_id}/delete/",
                params={"collection_position": collection_position}
            ) as response:
                if response.status == 204:
                    return DeleteResult()
                else:
                    response_body = await response.json()
                    return DeleteResult(error=response_body.get("message"))
    #
    # async def copy(self, value_id: str, table_id: str, collection_position: int = 1):
    #     response_body, status_code = await self.retrieve(value_id=value_id, collection_position=collection_position)
    #     if status_code == 200:
    #         response_body, status_code = await self.create(
    #             {"values": response_body.get("values"), "table_id": table_id,
    #              "collection_position": collection_position, "index": value_id}
    #         )
    #         return response_body, status_code
