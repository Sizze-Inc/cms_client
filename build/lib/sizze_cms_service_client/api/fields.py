import aiohttp
from sizze_cms_service_client.api.collection import CmsClient


class FieldsClient(CmsClient):
    async def create(self, field: dict, table: str, name: str, index: str = None, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.base_url + "field/create/",
                params={"collection_position": collection_position},
                json={
                    "field": field,
                    "table": table,
                    "name": name,
                    "index": index
                }
            ) as response:
                response_body = await response.json()
                if response.status == 201:
                    return response_body.get("_id")
                else:
                    return response_body

    async def retrieve(self, field_id: str, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "field/retrieve/",
                params={"field_id": field_id, "collection_position": collection_position}
            ) as response:
                response_body = await response.json()
                return response_body

    async def list(self, table_id: str = None, filtering: dict = None,
                   skip: int = None, limit: int = None, collection_position: int = 1):
        params = {}
        if table_id:
            params["table_id"] = table_id
        # if filtering is None:
        #     params["filtering"] = {}
        if skip:
            params["skip"] = skip
        if limit:
            params["limit"] = limit
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "field/list/",
                params=params
            ) as response:
                response_body = await response.json()
                return response_body

    async def update(self, field_id: str, field: dict, position: int, name: str,
                     table_id: str = None, storage_id: str = None, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            data = {
                "field": field,
                "name": name,
                "position": position
            }
            if table_id:
                data["table"] = table_id
            if storage_id:
                data["storage"] = storage_id

            async with session.put(
                url=self.base_url + f"field/{field_id}/update/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    return response_body.get("_id")
                else:
                    return response_body

    async def delete(self, field_id: str, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=self.base_url + f"field/{field_id}/delete/",
                params={"collection_position": collection_position}
            ) as response:
                if response.status == 200:
                    return True
                else:
                    return False

    async def copy(self, field_id: str, table_id: str, collection_position: int = 1):
        original_field = await self.retrieve(field_id=field_id, collection_position=collection_position)
        copy_field = await self.create(field=original_field.get("field"), table=table_id,
                                       name=original_field.get("name"), index=field_id)
        return copy_field
