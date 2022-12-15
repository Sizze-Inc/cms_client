import aiohttp
from sizze_cms_service_client.api.collection import CmsClient
from sizze_cms_service_client.api.fields import FieldsClient


class TableClient(CmsClient):
    async def create(self, data: dict, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.base_url + "table/create/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def retrieve(self, table_id: str, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "table/retrieve/",
                params={"table_id": table_id, "collection_position": collection_position}
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def related_retrieve(self, table_id, collection_position: int = 1, table_path=None, checked_tables=None):
        if table_path is None:
            table_path = []
        if checked_tables is None:
            checked_tables = set()
        checked_tables.add(table_id)
        fields_client = FieldsClient()
        fields_client.set_base_url(base_url=self.base_url)
        table_body, table_status_code = await self.retrieve(table_id=table_id, collection_position=collection_position)
        if table_status_code == 200:
            fields_body, fields_status_code = await fields_client.list(
                table_id=table_id, collection_position=collection_position
            )
            if fields_status_code == 200:
                table_body["fields"] = fields_body
                table_path.append(table_body)
                for field in fields_body:
                    if field["field"]["to_table"] and field["field"]["to_table"] not in checked_tables:
                        await self.related_retrieve(
                            table_id=field["field"]["to_table"], table_path=table_path, checked_tables=checked_tables
                        )
                return table_path

    async def list(self, **params):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "table/list/",
                params=params
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def update(self, table_id: str, data: dict, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url=self.base_url + f"table/{table_id}/update/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def delete(self, table_id: str, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=self.base_url + f"table/{table_id}/delete/",
                params={"collection_position": collection_position}
            ) as response:
                if response.status == 204:
                    return None, response.status
                else:
                    response_body = await response.json()
                    return response_body, response.status

    async def copy(self, table_id: str, to_storage_id: str, collection_position: int = 1):
        response_body, status_code = await self.retrieve(table_id=table_id, collection_position=collection_position)
        if status_code == 200:
            response_body, status_code = await self.create(
                {"storage_id": to_storage_id, "table_name": response_body.get("name"), "index": table_id}
            )
            return response_body, status_code
