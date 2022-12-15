import aiohttp
from sizze_cms_service_client.api.collection import CmsClient
from sizze_cms_service_client.api.tables import TableClient
from sizze_cms_service_client.api.fields import FieldsClient
from sizze_cms_service_client.api.values import ValuesClient


class StorageClient(CmsClient):
    async def create(self, data: dict, collection_position: int = 1, template: dict = None):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.base_url + "storage/create/",
                params={"collection_position": collection_position},
                json=data,
            ) as response:
                response_body = await response.json()
                if response.status == 201 and template:
                    storage_id = response_body.get("_id")
                    await self.template_create(template=template, storage=storage_id)
                return response_body, response.status

    async def retrieve(self, **params):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "storage/retrieve/",
                params=params
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def list(self, **params):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "storage/list/",
                params=params
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def update(self, data: dict, storage_id, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url=self.base_url + f"storage/{storage_id}/update/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def delete(self, storage_id: str, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=self.base_url + f"storage/{storage_id}/delete/",
                params={"collection_position": collection_position}
            ) as response:
                if response.status == 204:
                    return None, response.status
                else:
                    response_body = await response.json()
                    return response_body, response.status

    async def template_create(self, template, storage, collection_position: int = 1):
        split_val = "$"
        for table in template:
            table_client = TableClient(base_url=self.base_url)
            response_body, status_code = await table_client.create(
                data={"storage_id": storage, "table_name": table.get("name")}, collection_position=collection_position
            )
            if status_code == 201:
                table_id = response_body.get("_id")
                table["_id"] = table_id
                fields = table.get("fields")
                values = table.get("values")
                if isinstance(fields, list) and len(fields) > 0:
                    field_client = FieldsClient(base_url=self.base_url)
                    for field in fields:
                        field["table"] = table_id
                        if field["field"]["to_table"] is not None:
                            to_table = field["field"]["to_table"].split(split_val)
                            table = next(item for item in template if item["name"] == to_table[0])
                            field["field"]["to_table"] = table[to_table[1]]
                        field_create, _ = await field_client.create(
                            data={"table": table_id, "field": field["field"], "name": field["name"]}
                        )
                        field["_id"] = field_create

                if isinstance(values, list) and len(values) > 0:
                    value_client = ValuesClient(base_url=self.base_url)
                    for value in values:
                        value["table"] = table_id
                        value["new_values"] = {}
                        for key, val in value["values"].items():
                            new_key = key.split(split_val)
                            if isinstance(val, str):
                                new_val = val.split(split_val)
                            else:
                                new_val = None

                            if len(new_key) > 1:
                                table = next(item for item in template if item["name"] == new_key[0])
                                new_key = table[new_key[1]][int(new_key[2])][new_key[3]]
                            else:
                                new_key = key

                            if new_val and len(new_val) > 1:
                                table = next(item for item in template if item["name"] == new_val[0])
                                new_val = table[new_val[1]][int(new_val[2])][new_val[3]]
                            else:
                                new_val = val

                            value["new_values"][new_key] = new_val

                        value_create, _ = await value_client.create(
                            data={"values": value.get("new_values"), "table_id": table_id}
                        )
                        value["_id"] = value_create
