import aiohttp
from sizze_cms_service_client.api.collection import CmsClient


class StorageClient(CmsClient):
    async def create(self, project_id: int, users: list = None, tables: list = None, index: str = None,
                     collection_position: int = 1):
        if tables is None:
            tables = []
        if users is None:
            users = []
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.base_url + "storage/create/",
                params={"collection_position": collection_position},
                json={
                    "project_id": project_id,
                    "users": users,
                    "tables": tables,
                    "index": index
                }
            ) as response:
                response_body = await response.json()
                if response.status == 201:
                    return response_body.get("_id")
                else:
                    return response_body

    async def retrieve(self, storage_id: str = None, project_id: str = None, collection_position: int = 1):
        params = {"collection_position": collection_position}
        if storage_id:
            params["storage_id"] = storage_id
        if project_id:
            params["project_id"] = project_id
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "storage/retrieve/",
                params=params
            ) as response:
                response_body = await response.json()
                return response_body

    async def list(self, user_id: str = None, skip: int = None, limit: int = None, collection_position: int = 1):
        params = {"collection_position": collection_position}
        if user_id:
            params["user_id"] = user_id
        if skip:
            params["skip"] = skip
        if limit:
            params["limit"] = limit
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "storage/list/",
                params=params
            ) as response:
                response_body = await response.json()
                return response_body

    async def update(self, storage_id: str, storage_map: dict, project_id: int = None, users: list = None,
                     tables: list = None, collection_position: int = 1):
        data = {}
        if project_id:
            data["project_id"] = project_id
        if users:
            data["users"] = users
        if tables:
            data["tables"] = tables
        if storage_map:
            data["map"] = storage_map

        async with aiohttp.ClientSession() as session:
            async with session.put(
                url=self.base_url + f"storage/{storage_id}/update/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    return response_body.get("_id")
                else:
                    return response_body

    async def delete(self, storage_id: str, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=self.base_url + f"storage/{storage_id}/delete/",
                params={"collection_position": collection_position}
            ) as response:
                if response.status == 200:
                    return True
                else:
                    return False
