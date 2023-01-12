import aiohttp
from sizze_cms_service_client.api.collection import CmsClient, RetrieveResult


class UserClient(CmsClient):
    async def auth(self, data: dict, **params) -> RetrieveResult:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=self.base_url + "user/auth/",
                    params=params,
                    json=data
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    _id = response_body.get("_id")
                    value_response = RetrieveResult(_id=_id, data=response_body)
                else:
                    value_response = RetrieveResult(result=False, error=response_body.get("message"))
                return value_response
