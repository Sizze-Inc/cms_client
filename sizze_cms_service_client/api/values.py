from sizze_cms_service_client.api.collection import CmsClient, ServerResponse


class ValuesClient(CmsClient):
    async def create(self, data: dict) -> ServerResponse:
        self.path = "value/create/"
        response = await self.send_request(method="post", data=data)
        return response

    async def retrieve(self, value_id, depth=None) -> ServerResponse:
        self.path = f"value/retrieve/"
        response = await self.send_request(method="get", value_id=value_id, depth=depth)
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

    async def multiple_delete(self, value_ids: list) -> ServerResponse:
        self.path = f"value/multiple_delete/"
        response = await self.send_request(method="delete", data=value_ids)
        return response


value_client = ValuesClient()
