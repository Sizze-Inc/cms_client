from sizze_cms_service_client.api.collection import CmsClient, ServerResponse


class UserClient(CmsClient):
    async def auth(self, data: dict, storage_id) -> ServerResponse:
        self.path = "user/auth/"
        response = await self.send_request(method="post", data=data, storage_id=storage_id)
        return response


user_client = UserClient()
