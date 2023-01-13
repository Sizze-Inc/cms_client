import copy
from sizze_cms_service_client.api.tables import table_client
from sizze_cms_service_client.api.fields import field_client
from sizze_cms_service_client.api.values import value_client
from sizze_cms_service_client.api.collection import ServerError


class Templater:
    def __init__(self):
        self.split_char = "$"

    async def template_create(self, template, storage):
        """First template loop"""
        await self.first_template_loop(storage=storage, template=template)
        """Second template loop"""
        await self.second_template_loop(template=template)
        """Third template loop"""
        await self.third_template_loop(template=template)

    async def first_template_loop(self, template, storage):
        counter = 0
        for table in template:
            try:
                created_table_response = await table_client.create(
                    data={"storage": storage, "name": table.get("name"), "type": table.get("type")}
                )
            except ServerError:
                return False

            table_response = await table_client.retrieve(
                table_id=created_table_response.id,
            )
            table_object = table_response.data
            table_object["fields"] = table["fields"]
            table_object["values"] = table["values"]
            table_object["user_options"] = table.get("user_options")
            template[counter] = table_object
            counter += 1
        return True

    async def second_template_loop(self, template):
        """Вторичный цикл, создает первичные поля и значение"""
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

                        try:
                            field_create_response = await field_client.create(
                                data={"table": table_id, "field": copy_field_options, "name": field["name"]}
                            )
                        except ServerError:
                            return False

                        field_retrieve_retrieve = await field_client.retrieve(
                            field_id=field_create_response.id
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
                        try:
                            value_create_response = await value_client.create(
                                data=data_value
                            )
                        except ServerError:
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
                        data={"type": table["type"], "user_options": user_options}
                    )
            table_counter += 1

    async def third_template_loop(self, template):
        for table in template:
            table_id = table.get("_id")
            if table_id:
                fields = table.get("fields")
                values = table.get("values")
                for field in fields:
                    """Убрать related field из обновления"""
                    await field_client.update(
                        field_id=field.get("_id"), data=field
                    )
                for value in values:
                    child_value: dict = value.get("values")
                    for field, val in child_value.copy().items():
                        if isinstance(val, str) and "$" in val:
                            new_val = await self.get_val_from_template(field_val=val, template=template)
                            if new_val:
                                child_value[field] = new_val.get("_id")
                    await value_client.update(
                        value_id=value.get("_id"), data=value
                    )

    async def get_val_from_template(self, field_val, template):
        field_val_split = field_val.split(self.split_char)
        if len(field_val_split) == 4:
            field_table_id = int(field_val_split[0])
            field_id = int(field_val_split[2])
            field = template[field_table_id][field_val_split[1]][field_id]
            return field
