import aiohttp, copy
from sizze_cms_service_client.api.collection import CmsClient, CreateUpdateResult, RetrieveResult,\
    ListResult, DeleteResult
from sizze_cms_service_client.api.tables import TableClient
from sizze_cms_service_client.api.fields import FieldsClient
from sizze_cms_service_client.api.values import ValuesClient


class StorageClient(CmsClient):
    async def create(self, data: dict, template: dict = None) -> CreateUpdateResult:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.base_url + "storage/create/",
                json=data,
            ) as response:
                response_body = await response.json()
                if response.status == 201 and template:
                    storage_id = response_body.get("_id")
                    await self.template_create(template=template, storage=storage_id)
                    storage_response = CreateUpdateResult(_id=storage_id)
                else:
                    storage_response = CreateUpdateResult(result=False, error=response_body.get("message"))
                return storage_response

    async def retrieve(self, **params) -> RetrieveResult:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "storage/retrieve/",
                params=params
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    storage_id = response_body.get("_id")
                    storage_response = RetrieveResult(_id=storage_id, data=response_body)
                else:
                    storage_response = RetrieveResult(result=False, error=response_body.get("message"))
                return storage_response

    async def retrieve_storage_by_table(self, table_id: str, table_object: dict = None) -> RetrieveResult:
        if table_object and table_object.get("storage"):
            storage_id = table_object.get("storage")
        else:
            table_client = TableClient(base_url=self.base_url)
            table, _ = await table_client.retrieve(table_id=table_id)
            storage_id = table.get("storage")
        storage = await self.retrieve(storage_id=storage_id)
        return storage

    async def retrieve_storage_by_field_id(self, field_id: str, field_object: dict = None) -> RetrieveResult:
        if field_object and field_object.get("table"):
            table_id = field_object.get("table")
        else:
            field_client = FieldsClient(base_url=self.base_url)
            field, _ = await field_client.retrieve(field_id=field_id)
            table_id = field.get("table")
        storage = await self.retrieve_storage_by_table(table_id=table_id)
        return storage

    async def retrieve_storage_by_value_id(self, value_id: str, value_object: dict = None) -> RetrieveResult:
        if value_object and value_object.get("table"):
            table_id = value_object.get("table")
        else:
            value_client = ValuesClient(base_url=self.base_url)
            value, _ = await value_client.retrieve(value_id=value_id)
            table_id = value.get("table")
        storage = await self.retrieve_storage_by_table(table_id=table_id)
        return storage

    async def list(self, **params) -> ListResult:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.base_url + "storage/list/",
                params=params
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    storage_ids = [storage.get("_id") for storage in response_body]
                    storages_response = ListResult(data=response_body, _ids=storage_ids)
                else:
                    storages_response = ListResult(result=False, error=response_body.get("message"))
                return storages_response

    async def update(self, data: dict, storage_id, collection_position: int = 1) -> CreateUpdateResult:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url=self.base_url + f"storage/{storage_id}/update/",
                params={"collection_position": collection_position},
                json=data
            ) as response:
                response_body = await response.json()
                if response.status == 200:
                    storage_id = response_body.get("_id")
                    storage_response = CreateUpdateResult(_id=storage_id)
                else:
                    storage_response = CreateUpdateResult(result=False, error=response_body.get("message"))
                return storage_response

    async def delete(self, storage_id: str, collection_position: int = 1) -> DeleteResult:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=self.base_url + f"storage/{storage_id}/delete/",
                params={"collection_position": collection_position}
            ) as response:
                if response.status == 204:
                    return DeleteResult()
                else:
                    response_body = await response.json()
                    return DeleteResult(error=response_body.get("message"))

    async def template_create(self, template, storage, collection_position: int = 1):
        """First template loop"""
        await self.first_template_loop(storage=storage, template=template, collection_position=collection_position)
        """Second template loop"""
        await self.second_template_loop(storage=storage, template=template, collection_position=collection_position)
        """Third template loop"""
        await self.third_template_loop(storage=storage, template=template, collection_position=collection_position)

    async def first_template_loop(self, template, storage, collection_position):
        table_client = TableClient(base_url=self.base_url)
        counter = 0
        for table in template:
            created_table_response = await table_client.create(
                data={"storage": storage, "name": table.get("name"), "type": table.get("type")},
                collection_position=collection_position
            )
            if created_table_response.result is False:
                return False
            table_response = await table_client.retrieve(
                table_id=created_table_response.id,
                collection_position=collection_position
            )
            table_object = table_response.data
            table_object["fields"] = table["fields"]
            table_object["values"] = table["values"]
            table_object["user_options"] = table.get("user_options")
            template[counter] = table_object
            counter += 1
        return True

    async def second_template_loop(self, template, storage, collection_position):
        """Вторичный цикл, создает первичные поля и значение"""
        field_client = FieldsClient(base_url=self.base_url)
        value_client = ValuesClient(base_url=self.base_url)
        table_client = TableClient(base_url=self.base_url)
        table_counter = 0
        for table in template:
            table_id = table.get("_id")
            if table_id:
                """Создаются первичные поля, без (default, related_field, object_field, return_field, required=False)"""
                fields = table.get("fields")
                field_counter = 0
                if isinstance(fields, list) and len(fields) > 0:
                    for field in fields:
                        field["table"] = table_id
                        if field["field"]["to_table"] is not None:
                            to_table_split = field["field"]["to_table"].split(self.split_char)
                            """Разделяем значение по раздилителю"""
                            if len(to_table_split) == 2 and to_table_split[1] == "_id":
                                to_table_id = int(to_table_split[0])
                                """Проверяю условия разделитиля для to_table"""
                                field["field"]["to_table"] = template[to_table_id].get("_id")
                        """
                        Создается копия field field так как при первичном создании required False,
                        а после при третьем цикле будут установлены required из шаблона
                        """
                        copy_field_options = field["field"].copy()
                        copy_field_options["required"] = False
                        copy_field_options["default"] = None
                        copy_field_options["object_field"] = "_id"
                        copy_field_options["return_field"] = ["_id"]
                        field_create_response = await field_client.create(
                            data={"table": table_id, "field": copy_field_options, "name": field["name"]},
                            collection_position=collection_position
                        )
                        if field_create_response.result is False:
                            return False
                        field_retrieve_retrieve = await field_client.retrieve(
                            field_id=field_create_response.id,
                            collection_position=collection_position
                        )
                        field_data = field_retrieve_retrieve.data
                        field_data["field"]["required"] = field["field"]["required"]
                        field_data["field"]["default"] = field["field"]["default"]
                        field_data["field"]["object_field"] = field["field"]["object_field"]
                        field_data["field"]["return_field"] = field["field"]["return_field"]
                        template[table_counter]["fields"][field_counter] = field_data

                        field_counter += 1

                """Создаются первичные значения"""
                values = table.get("values")
                """Создается копия values, которая будет обновлятся в цикле"""
                if isinstance(values, list) and len(values) > 0:
                    for parent_value in values:
                        parent_value["table"] = table_id
                        child_values = parent_value.get("values")
                        data_value = copy.deepcopy(parent_value)
                        if isinstance(child_values, dict):
                            for field, value in child_values.copy().items():
                                template_field = await self.get_val_from_template(
                                    field_val=field, template=template
                                )
                                if template_field and template_field["field"].get("to_table"):
                                    data_value["values"][template_field.get("_id")] = None
                                    parent_value["values"][template_field.get("_id")] = parent_value["values"][field]
                                else:
                                    """Если значение не отношение, то устанавливается из шаблона, иначе по Null"""
                                    data_value["values"][template_field.get("_id")] = value
                                    parent_value["values"][template_field.get("_id")] = value
                                del data_value["values"][field]
                                del parent_value["values"][field]
                        """Создаются значения"""
                        value_create_response = await value_client.create(
                            data=data_value,
                            collection_position=collection_position
                        )
                        if value_create_response.result is False:
                            return False
                        parent_value["_id"] = value_create_response.id

                if table.get("user_options") and isinstance(table.get("user_options"), dict):
                    user_options = table.get("user_options")
                    login_field = await self.get_val_from_template(
                        field_val=user_options.get("login_field"), template=template
                    )
                    password_field = await self.get_val_from_template(
                        field_val=user_options.get("password_field"), template=template
                    )
                    user_options["login_field"] = login_field.get("_id")
                    user_options["password_field"] = password_field.get("_id")
                    table["user_options"] = user_options
                    await table_client.update(
                        table_id=table_id,
                        data={"type": table["type"], "user_options": user_options},
                        collection_position=collection_position
                    )
            table_counter += 1

    async def third_template_loop(self, template, collection_position):
        field_client = FieldsClient(base_url=self.base_url)
        value_client = ValuesClient(base_url=self.base_url)
        for table in template:
            table_id = table.get("_id")
            if table_id:
                fields = table.get("fields")
                values = table.get("values")
                for field in fields:
                    """Убрать related field из обновления"""
                    await field_client.update(
                        field_id=field.get("_id"), data=field, collection_position=collection_position
                    )
                for value in values:
                    child_value: dict = value.get("values")
                    for field, val in child_value.copy().items():
                        if isinstance(val, str) and "$" in val:
                            new_val = await self.get_val_from_template(field_val=val, template=template)
                            if new_val:
                                child_value[field] = new_val.get("_id")
                    await value_client.update(
                        value_id=value.get("_id"), data=value, collection_position=collection_position
                    )

    async def get_val_from_template(self, field_val, template):
        field_val_split = field_val.split(self.split_char)
        if len(field_val_split) == 4:
            field_table_id = int(field_val_split[0])
            field_id = int(field_val_split[2])
            field = template[field_table_id][field_val_split[1]][field_id]
            return field
