import aiohttp
from sizze_cms_service_client.api.collection import CmsClient
from sizze_cms_service_client.api.tables import TableClient
from sizze_cms_service_client.api.fields import FieldsClient
from sizze_cms_service_client.api.values import ValuesClient


class StorageClient(CmsClient):
    async def create(self, project_id: int, users: list = None, tables: list = None, index: str = None,
                     collection_position: int = 1, template: dict = None):
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
                    response = response_body.get("_id")
                    if template:
                        await self.template_create(template=template, storage=response)
                else:
                    response = response_body

        return response

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

    async def template_create(self, template, storage):
        for table in template:
            table_client = TableClient(base_url=self.base_url)
            table_create = await table_client.create(storage_id=storage, table_name=table.get("name"))
            print(table_create)
            if table_create:
                fields = table.get("fields")
                values = table.get("values")
                if isinstance(fields, list) and len(fields) > 0:
                    field_client = FieldsClient(base_url=self.base_url)
                    for field in fields:
                        field["table"] = table_create
                        if field["field"]["to_table"] is not None:
                            to_table = field["field"]["to_table"].split(".")
                            field["field"]["to_table"] = template[to_table[0]][to_table[1]]
                        print("table: ", table_create)
                        print("field: ", field)
                        field_create = await field_client.create(
                            table=table_create, field=field["field"], name=field["name"]
                        )
                        print(field_create)
                        field["_id"] = field_create

                if isinstance(values, list) and len(values) > 0:
                    value_client = ValuesClient(base_url=self.base_url)
                    for value in values:
                        value["table"] = table_create
                        for key, val in value["values"].items():
                            new_key = key.strip(".")
                            new_val = val.strip(".")
                            if len(new_key) > 1:
                                table = next(item for item in template if item["name"] == new_key[0])
                                new_key = table[new_key[1]][new_key[2]][new_key[3]]
                            else:
                                new_key = key

                            if len(new_val) > 1:
                                table = next(item for item in template if item["name"] == new_val[0])
                                new_val = table[new_val[1]][new_val[2]][new_val[3]]
                            else:
                                new_val = val

                            del value["values"][key]
                            value["values"][new_key] = new_val

                        print("table: ", table_create)
                        print("values ", value.get("values"))
                        value_create = await value_client.create(
                            values=value.get("values"), table_id=table_create
                        )
                        print(value_create)
                        value["_id"] = value_create
