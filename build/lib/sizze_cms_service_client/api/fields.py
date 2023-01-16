from sizze_cms_service_client.api.collection import CmsClient, ServerResponse


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

    async def update(self, field_id: str, data: dict) -> ServerResponse:
        self.path = f"field/{field_id}/update/"
        response = await self.send_request(method="put", data=data)
        return response

    async def delete(self, field_id: str) -> ServerResponse:
        self.path = f"field/{field_id}/delete/"
        response = await self.send_request(method="delete", field_id=field_id)
        return response


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
