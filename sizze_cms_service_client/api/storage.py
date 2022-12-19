import aiohttp
from sizze_cms_service_client.api.collection import CmsClient
from sizze_cms_service_client.api.tables import TableClient
from sizze_cms_service_client.api.fields import FieldsClient
from sizze_cms_service_client.api.values import ValuesClient


class StorageClient(CmsClient):
    async def create(self, data: dict, collection_position: int = 1, template: dict = None):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.base_url + "storage/create/",
                params={"collection_position": collection_position},
                json=data,
            ) as response:
                response_body = await response.json()
                if response.status == 201 and template:
                    storage_id = response_body.get("_id")
                    await self.template_create(template=template, storage=storage_id)
                return response_body, response.status

    async def retrieve(self, **params):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "storage/retrieve/",
                params=params
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def list(self, **params):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "storage/list/",
                params=params
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def update(self, data: dict, storage_id, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url=self.base_url + f"storage/{storage_id}/update/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                return response_body, response.status

    async def delete(self, storage_id: str, collection_position: int = 1):
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=self.base_url + f"storage/{storage_id}/delete/",
                params={"collection_position": collection_position}
            ) as response:
                if response.status == 204:
                    return None, response.status
                else:
                    response_body = await response.json()
                    return response_body, response.status

    async def template_create(self, template, storage, collection_position: int = 1):
        """First template loop"""
        await self.first_template_loop(storage=storage, template=template, collection_position=collection_position)
        print(template)

        # """Second template loop"""
        # await self.second_template_loop(storage=storage, template=template, collection_position=collection_position)
        # print(template)
        #
        # """Third template loop"""
        # await self.third_template_loop(storage=storage, template=template, collection_position=collection_position)
        # print(template)

    async def first_template_loop(self, template, storage, collection_position):
        table_client = TableClient(base_url=self.base_url)
        for table in template:
            response_body, status_code = await table_client.create(
                data={"storage": storage, "name": table.get("name"), "type": table.get("type")},
                collection_position=collection_position
            )
            if status_code != 200:
                return False
            table["_id"] = table.get("_id")
        return True

    async def second_template_loop(self, template, storage, collection_position):
        """Вторичный цикл, создает первичные поля и значение"""
        field_client = FieldsClient(base_url=self.base_url)
        value_client = ValuesClient(base_url=self.base_url)
        table_client = TableClient(base_url=self.base_url)
        for table in template:
            table_id = table.get("_id")
            if table_id:
                """Создаются первичные поля, без (default, related_field, object_field, return_field, required=False)"""
                fields = table.get("fields")
                if isinstance(fields, list) and len(fields) > 0:
                    for field in fields:
                        field["table"] = table_id
                        if field["field"]["to_table"] is not None:
                            to_table = field["field"]["to_table"].split(self.split_char)
                            """Разделяем значение по раздилителю"""
                            if len(to_table) == 2 and int(to_table[0]) and to_table[1] == "_id":
                                """Проверяю условия разделитиля для to_table"""
                                field["field"]["to_table"] = template[to_table[0]]
                        """
                        Создается копия field field так как при первичном создании required False,
                        а после при третьем цикле будут установлены required из шаблона
                        """
                        copy_field_options = field["field"].copy()
                        copy_field_options["required"] = False
                        copy_field_options["default"] = None
                        copy_field_options["object_field"] = "_id"
                        copy_field_options["return_field"] = ["_id"]
                        field_create, status_code = await field_client.create(
                            data={"table": table_id, "field": copy_field_options, "name": field["name"]}
                        )
                        if status_code != 200:
                            return False
                        field["_id"] = field_create.get("_id")
                template["fields"] = fields

                """Создаются первичные значения"""
                values = table.get("values")
                """Создается копия values, которая будет обновлятся в цикле"""
                copy_values = []
                if isinstance(values, list) and len(values) > 0:
                    for parent_value in values:
                        copy_parent_value = parent_value.copy()
                        copy_parent_value["table"] = table_id
                        child_values = parent_value.get("values")
                        if isinstance(child_values, dict):
                            for field, value in child_values.items():
                                template_field = self.get_field_from_template(
                                    field_val=field, template=template
                                )
                                if template_field:
                                    copy_parent_value["values"][template_field] = None

                                split_value = value.split(self.split_char)
                                """Если значение не отношение, то устанавливается из шаблона, иначе по Null"""
                                if len(split_value) == 1:
                                    copy_parent_value["values"][template_field] = value
                        """Создаются значения"""
                        value_create, status_code = await value_client.create(
                            data=copy_parent_value
                        )
                        if status_code != 200:
                            return False
                        copy_parent_value["_id"] = value_create.get("_id")
                        copy_values.append(copy_parent_value)
                        template["values"] = copy_values

                if table.get("user_options") and isinstance(table.get("user_options"), dict):
                    user_options = table.get("user_options")
                    user_options["login_field"] = self.get_field_from_template(
                        field_val=user_options.get("login_field"), template=template
                    )
                    user_options["password_field"] = self.get_field_from_template(
                        field_val=user_options.get("password_field"), template=template
                    )
                    table["user_options"] = user_options
                    response_body, status_code = await table_client.update(
                        table_id=table_id,
                        data={"user_options": user_options},
                        collection_position=collection_position
                    )
                    if status_code != 200:
                        return False

    async def third_template_loop(self, template, storage, collection_position):
        field_client = FieldsClient(base_url=self.base_url)
        value_client = ValuesClient(base_url=self.base_url)
        for table in template:
            table_id = table.get("_id")
            if table_id:
                fields = table.get("fields")
                values = table.get("values")
                for field in fields:
                    await field_client.update(
                        field_id=field.get("_id"), data=field, collection_position=collection_position
                    )
                for value in values:
                    await value_client.update(
                        value_id=value.get("_id"), data=value, collection_position=collection_position
                    )

    async def get_field_from_template(self, field_val, template):
        field_val_split = field_val.split(self.split_char)
        if len(field_val_split) == 4:
            field_table_id = int(field_val_split[0])
            field_id = int(field_val_split[2])
            field = template[field_table_id][field_val_split[1]][field_id]
            return field
