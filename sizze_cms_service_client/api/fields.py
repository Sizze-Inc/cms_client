import aiohttp
from sizze_cms_service_client.api.collection import CmsClient, CreateUpdateResult, RetrieveResult,\
    ListResult, DeleteResult


class FieldsClient(CmsClient):
    async def create(self, data: dict, collection_position: int = 1) -> CreateUpdateResult:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.base_url + "field/create/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                if response.status == 201:
                    _id = response_body.get("_id")
                    field_response = CreateUpdateResult(_id=_id)
                else:
                    field_response = CreateUpdateResult(result=False, error=response_body.get("message"))
                return field_response

    async def retrieve(self, field_id: str, collection_position: int = 1) -> RetrieveResult:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "field/retrieve/",
                params={"field_id": field_id, "collection_position": collection_position}
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    _id = response_body.get("_id")
                    field_response = RetrieveResult(_id=_id, data=response_body)
                else:
                    field_response = RetrieveResult(result=False, error=response_body.get("message"))
                return field_response

    async def list(self, **params) -> ListResult:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "field/list/",
                params=params
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    _ids = [field.get("_id") for field in response_body]
                    field_response = ListResult(data=response_body, _ids=_ids)
                else:
                    field_response = ListResult(result=False, error=response_body.get("message"))
                return field_response

    async def update(self, field_id: str, data: dict, collection_position: int = 1) -> CreateUpdateResult:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url=self.base_url + f"field/{field_id}/update/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    _id = response_body.get("_id")
                    field_response = CreateUpdateResult(_id=_id)
                else:
                    field_response = CreateUpdateResult(result=False, error=response_body.get("message"))
                return field_response

    async def delete(self, field_id: str, collection_position: int = 1) -> DeleteResult:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=self.base_url + f"field/{field_id}/delete/",
                params={"collection_position": collection_position}
            ) as response:
                if response.status == 204:
                    return DeleteResult()
                else:
                    response_body = await response.json()
                    return DeleteResult(error=response_body.get("message"))

    # async def copy(self, field_id: str, table_id: str, collection_position: int = 1):
    #     response_body, status_code = await self.retrieve(field_id=field_id, collection_position=collection_position)
    #     if status_code == 200:
    #         response_body, status_code = await self.create(
    #             {
    #                 "field": response_body.get("field"), "table": table_id,
    #                 "name": response_body.get("name"), "index": field_id
    #             }
    #         )
    #         return response_body, status_code
