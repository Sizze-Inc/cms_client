import aiohttp
from sizze_cms_service_client.api.collection import CmsClient


class TableClient(CmsClient):
    async def create(self, storage_id: str, table_name: str, fields: list = None, values: list = None,
                     index: str = None, collection_position: int = None):
        data = {
            "storage_id": storage_id,
            "name": table_name,
            "index": index
        }
        if fields:
            data["fields"] = fields
        if values:
            data["values"] = values

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.base_url + "table/create/",
                params={"collection_position": collection_position},
                data=data
            ) as response:
                response_body = await response.json()
                if response.status == 201:
                    return response_body.get("_id")
                elif response_body.get("result") is False:
                    return response_body.get("message")
                else:
                    return response_body

    async def retrieve(self, table_id: str, collection_position: int = None):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "table/retrieve/",
                params={"table_id": table_id, "collection_position": collection_position}
            ) as response:
                response_body = await response.json()
                if response_body.get("result") is False:
                    return response_body.get("message")
                else:
                    return response_body

    async def list(self, storage_id: str = None, skip: int = None, limit: int = None, collection_position: int = None):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "table/list/",
                params={
                    "storage_id": storage_id, "skip": skip, "limit": limit, "collection_position": collection_position
                }
            ) as response:
                response_body = await response.json()
                if response_body.get("result") is False:
                    return response_body.get("message")
                else:
                    return response_body

    async def update(self, table_id: str, name: str = None, position: int = None,
                     fields: list = None, values: list = None, collection_position: int = None):
        async with aiohttp.ClientSession() as session:
            data = {}
            if name:
                data["name"] = name
            if position:
                data["position"]: position
            if fields:
                data["fields"] = fields
            if values:
                data["values"] = values

            async with session.put(
                url=self.base_url + f"table/{table_id}/update/",
                params={"collection_position": collection_position},
                data=data
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    return response_body.get("_id")
                elif response_body.get("result") is False:
                    return response_body.get("message")
                else:
                    return response_body

    async def delete(self, table_id: str, collection_position: int = None):
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=self.base_url + f"table/{table_id}/delete/",
                params={"collection_position": collection_position}
            ) as response:
                if response.status == 200:
                    return True
                else:
                    return False

    async def copy(self, table_id: str, to_storage_id: str, collection_position: int = None):
        original_table = await self.retrieve(table_id=table_id, collection_position=collection_position)
        copy_table = await self.create(storage_id=to_storage_id, table_name=original_table.get("name"), index=table_id)
        return copy_table
