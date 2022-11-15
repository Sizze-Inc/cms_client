import aiohttp
from sizze_cms_service_client.api.collection import CmsClient


class ValuesClient(CmsClient):
    async def create(self, values: dict, table_id: str, index: str = None, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.base_url + "values/create/",
                params={"collection_position": collection_position},
                json={
                    "values": values,
                    "table": table_id,
                    "index": index
                }
            ) as response:
                response_body = await response.json()
                if response.status == 201:
                    return response_body.get("_id")
                else:
                    return response_body

    async def retrieve(self, value_id: str, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "value/retrieve/",
                params={"value_id": value_id, "collection_position": collection_position}
            ) as response:
                response_body = await response.json()
                return response_body

    async def list(self, table_id: str = None, storage_id: str = None, filtering: dict = None,
                   skip: int = None, limit: int = None, collection_position: int = 1):
        params = {"collection_position": collection_position}
        if storage_id:
            params["storage_id"] = storage_id
        if table_id:
            params["table_id"] = table_id
        if skip:
            params["skip"] = skip
        if limit:
            params["limit"] = limit
        if filtering is None:
            params["filtering"] = {}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "value/list/",
                params=params
            ) as response:
                response_body = await response.json()
                return response_body

    async def update(self, value_id: str, values: dict, position: int,
                     table_id: str = None, storage_id: str = None, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            data = {
                "values": values
            }
            if position:
                data["position"] = position
            if table_id:
                data["table"] = table_id
            if storage_id:
                data["storage"] = storage_id

            async with session.put(
                url=self.base_url + f"value/{value_id}/update/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    return response_body.get("_id")
                return response_body

    async def delete(self, value_id: str, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=self.base_url + f"value/{value_id}/delete/",
                params={"collection_position": collection_position}
            ) as response:
                if response.status == 200:
                    return True
                else:
                    return False

    async def copy(self, value_id: str, table_id: str, collection_position: int = 1):
        original_value = await self.retrieve(value_id=value_id, collection_position=collection_position)
        copy_value = await self.create(values=original_value.get("values"), table_id=table_id,
                                       collection_position=collection_position, index=value_id)
        return copy_value
