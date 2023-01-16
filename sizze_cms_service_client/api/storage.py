from sizze_cms_service_client.api.collection import CmsClient, ServerResponse
from sizze_cms_service_client.api.tables import TableClient
from sizze_cms_service_client.api.fields import FieldsClient
from sizze_cms_service_client.api.values import ValuesClient
from sizze_cms_service_client.api.templater import Templater


class StorageClient(CmsClient):
    async def create(self, data: dict, template: dict = None) -> ServerResponse:
        self.path = "storage/create/"
        response = await self.send_request(method="post", data=data)
        if template:
            templater = Templater()
            await templater.template_create(template=template, storage=response.id)
        return response

    async def retrieve(self, storage_id: str = None, project_id: str = None) -> ServerResponse:
        self.path = f"storage/retrieve/"
        response = await self.send_request(method="get", storage_id=storage_id, project_id=project_id)
        return response

    async def retrieve_storage_by_table(self, table_id: str, table_object: dict = None) -> ServerResponse:
        if table_object and table_object.get("storage"):
            storage_id = table_object.get("storage")
        else:
            table_client = TableClient()
            table, _ = await table_client.retrieve(table_id=table_id)
            storage_id = table.get("storage")
        storage = await self.retrieve(storage_id=storage_id)
        return storage

    async def retrieve_storage_by_field_id(self, field_id: str, field_object: dict = None) -> ServerResponse:
        if field_object and field_object.get("table"):
            table_id = field_object.get("table")
        else:
            field_client = FieldsClient()
            field, _ = await field_client.retrieve(field_id=field_id)
            table_id = field.get("table")
        storage = await self.retrieve_storage_by_table(table_id=table_id)
        return storage

    async def retrieve_storage_by_value_id(self, value_id: str, value_object: dict = None) -> ServerResponse:
        if value_object and value_object.get("table"):
            table_id = value_object.get("table")
        else:
            value_client = ValuesClient()
            value, _ = await value_client.retrieve(value_id=value_id)
            table_id = value.get("table")
        storage = await self.retrieve_storage_by_table(table_id=table_id)
        return storage

    async def list(self, user_id) -> ServerResponse:
        self.path = "storage/list/"
        response = await self.send_request(method="get", user_id=user_id)
        return response

    async def update(self, data: dict, storage_id) -> ServerResponse:
        self.path = f"storage/{storage_id}/update/"
        response = await self.send_request(method="put", data=data)
        return response

    async def delete(self, storage_id: str) -> ServerResponse:
        self.path = f"storage/{storage_id}/delete/"
        response = await self.send_request(method="delete", storage_id=storage_id)
        return response


storage_client = StorageClient()
