from sizze_cms_service_client.api.collection import CmsClient, ServerResponse


class ValuesClient(CmsClient):
    async def create(self, data: dict) -> ServerResponse:
        self.path = "value/create/"
        response = await self.send_request(method="post", data=data)
        return response

    async def retrieve(self, value_id) -> ServerResponse:
        self.path = f"value/retrieve/"
        response = await self.send_request(method="get", value_id=value_id)
        return response

    async def list(self, table_id, filtering=None, depth=None, sort=None, skip: int = 0, limit: int = 100)\
            -> ServerResponse:
        self.path = "value/list/"
        response = await self.send_request(method="get", table_id=table_id, filtering=filtering, depth=depth,
                                           sort=sort, skip=skip, limit=limit)
        return response

    async def search(self, table_id, value) -> ServerResponse:
        self.path = "value/search/"
        response = await self.send_request(method="get", table_id=table_id, value=value)
        return response

    async def update(self, value_id: str, data: dict) -> ServerResponse:
        self.path = f"value/{value_id}/update/"
        response = await self.send_request(method="put", data=data)
        return response

    async def delete(self, value_id: str) -> ServerResponse:
        self.path = f"value/{value_id}/delete/"
        response = await self.send_request(method="delete", value_id=value_id)
        return response


value_client = ValuesClient()
    #
    # async def copy(self, value_id: str, table_id: str, collection_position: int = 1):
    #     response_body, status_code = await self.retrieve(value_id=value_id, collection_position=collection_position)
    #     if status_code == 200:
    #         response_body, status_code = await self.create(
    #             {"values": response_body.get("values"), "table_id": table_id,
    #              "collection_position": collection_position, "index": value_id}
    #         )
    #         return response_body, status_code
