import aiohttp
from sizze_cms_service_client.api.collection import CmsClient


class UserClient(CmsClient):
    async def auth(self, data: dict, **params):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=self.base_url + "user/auth/",
                    params=params,
                    json=data
            ) as response:
                response_body = await response.json()
                return response_body, response.status
