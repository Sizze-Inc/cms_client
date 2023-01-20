from sizze_cms_service_client.api.collection import CmsClient, ServerResponse
from sizze_cms_service_client.api.tables import table_client


class FieldsClient(CmsClient):
    async def create(self, data: dict) -> ServerResponse:
        self.path = "field/create/"
        response = await self.send_request(method="post", data=data)
        return response

    async def retrieve(self, field_id: str) -> ServerResponse:
        self.path = f"field/retrieve/"
        response = await self.send_request(method="get", field_id=field_id)
        return response

    async def list(self, table_id, skip: int = 0, limit: int = 100, filtering=None) -> ServerResponse:
        self.path = "field/list/"
        response = await self.send_request(method="get", table_id=table_id, skip=skip, limit=limit, filtering=filtering)
        return response

    async def related_list(self, table_id) -> ServerResponse:
        self.path = "field/list_related/"
        response = await self.send_request(method="get", table_id=table_id)
        return response

    async def update(self, field_id: str, data: dict) -> ServerResponse:
        self.path = f"field/{field_id}/update/"
        response = await self.send_request(method="put", data=data)
        return response

    async def delete(self, field_id: str) -> ServerResponse:
        self.path = f"field/{field_id}/delete/"
        response = await self.send_request(method="delete", field_id=field_id)
        return response

    async def get_field_path(self, from_table, field_id, field_object=None):
        if field_object:
            table_id = field_object.get("table")
        else:
            field = await self.retrieve(field_id=field_id)
            table_id = field.data.get("table")

        table_path = await table_client.get_table_path(from_table=from_table, to_table=table_id)
        table_path_iterator = iter(table_path)
        if len(table_path) > 0:
            field_path = []
            next_item = next(table_path_iterator)
            for index in range(len(table_path)-1):
                this_item, next_item = next_item, next(table_path_iterator)
                field_path.append(
                    {
                        "table": {"id": this_item["table"], "index": this_item["table"]},
                        "field": {"id": next_item["field"], "index": next_item["field"]}
                    }
                )
            field_path.append(
                {
                    "table": {"id": table_id, "index": table_id},
                    "field": {"id": field_id, "index": field_id}
                }
            )
        else:
            field_path = []
        return field_path


field_client = FieldsClient()

    # async def copy(self, field_id: str, table_id: str, collection_position: int = 1):
    #     response_body, status_code = await self.retrieve(field_id=field_id, collection_position=collection_position)
    #     if status_code == 200:
    #         response_body, status_code = await self.create(
    #             {
    #                 "field": response_body.get("field"), "table": table_id,
    #                 "name": response_body.get("name"), "index": field_id
    #             }
    #         )
    #         return response_body, status_code
