import aiohttp
from sizze_cms_service_client.api.collection import CmsClient
from sizze_cms_service_client.api.tables import TableClient
from sizze_cms_service_client.api.values import ValuesClient


class UserClient(CmsClient):
    async def auth(self, data: dict, storage_id, collection_position: int = 1):
        table_client = TableClient(base_url=self.base_url)
        value_client = ValuesClient(base_url=self.base_url)
        user_table, status_code = await table_client.list(
            storage_id=storage_id, table_type="user"
        )
        if status_code == 200:
            if len(user_table) == 0:
                raise "User table not found"
            elif len(user_table) > 1:
                raise "Storage cant have more than one user table in project"
            user_table: dict = user_table[0]
            user_table_id = user_table.get("_id")
            login_field_id = user_table["user_options"]["login_field"]
            password_field_id = user_table["user_options"]["password_field"]
            users, status_code = await value_client.list(
                table_id=user_table_id,
                filtering={
                    login_field_id: data.get("login_field"),
                    password_field_id: data.get("password_field")
                }
            )
            if len(users) > 1:
                raise "Multiple user found"
            if len(users) == 0:
                raise "User with this credentials is not found"
            user = users[0]
            return user.get("_id")
