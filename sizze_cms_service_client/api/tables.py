import aiohttp
from sizze_cms_service_client.api.collection import CmsClient, CreateUpdateResult, RetrieveResult,\
    ListResult, DeleteResult
from sizze_cms_service_client.api.fields import FieldsClient


class TableClient(CmsClient):
    async def create(self, data: dict, collection_position: int = 1) -> CreateUpdateResult:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.base_url + "table/create/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                if response.status == 201:
                    table_id = response_body.get("_id")
                    table_response = CreateUpdateResult(_id=table_id)
                else:
                    table_response = CreateUpdateResult(result=False, error=response_body.get("message"))
                return table_response

    async def retrieve(self, table_id: str, collection_position: int = 1) -> RetrieveResult:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "table/retrieve/",
                params={"table_id": table_id, "collection_position": collection_position}
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    _id = response_body.get("_id")
                    table_response = RetrieveResult(_id=_id, data=response_body)
                else:
                    table_response = RetrieveResult(result=False, error=response_body.get("message"))
                return table_response

    async def related_retrieve(self, table_id, collection_position: int = 1, table_path=None, checked_tables=None):
        if table_path is None:
            table_path = []
        if checked_tables is None:
            checked_tables = set()
        checked_tables.add(table_id)
        fields_client = FieldsClient()
        fields_client.set_base_url(base_url=self.base_url)
        table_response = await self.retrieve(table_id=table_id, collection_position=collection_position)
        table_data = table_response.data
        if table_response.result:
            fields_response = await fields_client.list(
                table_id=table_id, collection_position=collection_position
            )
            if fields_response.result:
                fields_data = fields_response.data
                table_data["fields"] = fields_data
                table_path.append(table_data)
                for field in fields_data:
                    if field["field"]["to_table"] and field["field"]["to_table"] not in checked_tables:
                        await self.related_retrieve(
                            table_id=field["field"]["to_table"], table_path=table_path, checked_tables=checked_tables
                        )
                return table_path

    async def list(self, **params) -> ListResult:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "table/list/",
                params=params
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    _ids = [table.get("_id") for table in response_body]
                    table_response = ListResult(data=response_body, _ids=_ids)
                else:
                    table_response = ListResult(result=False, error=response_body.get("message"))
                return table_response

    async def update(self, table_id: str, data: dict, collection_position: int = 1) -> CreateUpdateResult:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url=self.base_url + f"table/{table_id}/update/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    _id = response_body.get("_id")
                    table_response = CreateUpdateResult(_id=_id)
                else:
                    table_response = CreateUpdateResult(result=False, error=response_body.get("message"))
                return table_response

    async def delete(self, table_id: str, collection_position: int = 1) -> DeleteResult:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=self.base_url + f"table/{table_id}/delete/",
                params={"collection_position": collection_position}
            ) as response:
                if response.status == 204:
                    return DeleteResult()
                else:
                    response_body = await response.json()
                    return DeleteResult(error=response_body.get("message"))

    # async def copy(self, table_id: str, to_storage_id: str, collection_position: int = 1):
    #     response_body, status_code = await self.retrieve(table_id=table_id, collection_position=collection_position)
    #     if status_code == 200:
    #         response_body, status_code = await self.create(
    #             {"storage_id": to_storage_id, "table_name": response_body.get("name"), "index": table_id}
    #         )
    #         return response_body, status_code
