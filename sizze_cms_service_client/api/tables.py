from sizze_cms_service_client.api.collection import CmsClient, ServerResponse
from sizze_cms_service_client.api.fields import FieldsClient


class TableClient(CmsClient):
    async def create(self, data: dict) -> ServerResponse:
        self.path = "table/create/"
        response = await self.send_request(method="post", data=data)
        return response

    async def retrieve(self, table_id: str) -> ServerResponse:
        self.path = f"table/retrieve/"
        response = await self.send_request(method="get", table_id=table_id)
        return response

    async def related_retrieve(self, table_id, table_path=None, checked_tables=None):
        if table_path is None:
            table_path = []
        if checked_tables is None:
            checked_tables = set()
        checked_tables.add(table_id)
        table_response = await self.retrieve(table_id=table_id)
        table_data = table_response.data

        fields_client = FieldsClient()
        fields_response = await fields_client.list(
            table_id=table_id
        )
        fields_data = fields_response.data
        table_data["fields"] = fields_data
        table_path.append(table_data)
        for field in fields_data:
            if field["field"]["to_table"] and field["field"]["to_table"] not in checked_tables:
                await self.related_retrieve(
                    table_id=field["field"]["to_table"], table_path=table_path, checked_tables=checked_tables
                )
        return table_path

    async def list(self, storage_id: str, skip=0, limit=100) -> ServerResponse:
        self.path = "table/list/"
        response = await self.send_request(method="get", storage_id=storage_id, skip=skip, limit=limit)
        return response

    async def update(self, table_id: str, data: dict) -> ServerResponse:
        self.path = f"table/{table_id}/update/"
        response = await self.send_request(method="put", data=data)
        return response

    async def delete(self, table_id: str) -> ServerResponse:
        self.path = f"table/{table_id}/delete/"
        response = await self.send_request(method="delete", table_id=table_id)
        return response


table_client = TableClient()

    # async def copy(self, table_id: str, to_storage_id: str, collection_position: int = 1):
    #     response_body, status_code = await self.retrieve(table_id=table_id, collection_position=collection_position)
    #     if status_code == 200:
    #         response_body, status_code = await self.create(
    #             {"storage_id": to_storage_id, "table_name": response_body.get("name"), "index": table_id}
    #         )
    #         return response_body, status_code
