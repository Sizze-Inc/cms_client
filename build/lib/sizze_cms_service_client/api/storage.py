import aiohttp
from sizze_cms_service_client.api.collection import CmsClient


class StorageClient(CmsClient):
    async def create(self, project_id: int, users: list = None, tables: list = None, index: str = None,
                     collection_position: int = None):
        if tables is None:
            tables = []
        if users is None:
            users = []
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.base_url + "storage/create/",
                params={"collection_position": collection_position},
                data={
                    "project_id": project_id,
                    "users": users,
                    "tables": tables,
                    "index": index
                }
            ) as response:
                response_body = await response.json()
                if response.status == 201:
                    return response_body.get("_id")
                elif response_body.get("result") is False:
                    return response_body.get("message")
                else:
                    return response_body

    async def retrieve(self, storage_id: str, collection_position: int = None):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "storage/retrieve/",
                params={"storage_id": storage_id, "collection_position": collection_position}
            ) as response:
                response_body = await response.json()
                if response_body.get("result") is False:
                    return response_body.get("message")
                else:
                    return response_body

    async def list(self, user_id: str = None, skip: int = None, limit: int = None, collection_position: int = None):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "storage/list/",
                params={"user_id": user_id, "skip": skip, "limit": limit, "collection_position": collection_position}
            ) as response:
                response_body = await response.json()
                if response_body.get("result") is False:
                    return response_body.get("message")
                else:
                    return response_body

    async def update(self, storage_id: str, project_id: int = None, users: list = None, tables: list = None,
                     collection_position: int = None):
        data = {}
        if project_id:
            data["project_id"] = project_id
        if users:
            data["users"] = users
        if tables:
            data["tables"] = tables

        async with aiohttp.ClientSession() as session:
            async with session.put(
                url=self.base_url + f"storage/{storage_id}/update/",
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

    async def delete(self, storage_id: str, collection_position: int = None):
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=self.base_url + f"storage/{storage_id}/delete/",
                params={"collection_position": collection_position}
            ) as response:
                if response.status == 200:
                    return True
                else:
                    return False
