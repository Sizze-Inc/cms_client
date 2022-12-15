from sizze_cms_service_client.api.collection import CmsClient
from sizze_cms_service_client.api import fields, storage, tables, values


class CopyClient(CmsClient):
    async def full_copy_storage(self, storage_id: str, to_project_id: int, users: list, collection_position: int = 1):
        storage_client = storage.StorageClient(base_url=self.base_url)
        table_client = tables.TableClient(base_url=self.base_url)

        storage_body, storage_status = await storage_client.retrieve(
            storage_id=storage_id, collection_position=collection_position
        )
        table_body, table_status = await table_client.list(
            storage_id=storage_body.get("_id"), collection_position=collection_position
        )

        storage_copy_body, storage_copy_status = await storage_client.create(
            {"project_id": to_project_id, "users": users, "index": storage_body.get("_id")}
        )
        tables_copy = []
        for original_table in table_body:
            table_copy = self.full_copy_table(
                table_id=original_table.get("_id"), to_storage_id=storage_copy_body,
                original_table=original_table, collection_position=collection_position
            )
            tables_copy.append(table_copy)
        await storage_client.update(
            storage_id=storage_copy_body.get("_id"), collection_position=collection_position,
            data={"tables": tables_copy}
        )

    async def full_copy_table(self, table_id: str, to_storage_id: str, original_table: dict = None,
                              collection_position: int = 1):
        table_client = tables.TableClient(base_url=self.base_url)
        value_client = values.ValuesClient(base_url=self.base_url)
        field_client = fields.FieldsClient(base_url=self.base_url)

        fields_copy = []
        values_copy = []
        if original_table is None:
            original_table_body, _ = await table_client.retrieve(table_id=table_id)

        table_copy, _ = await table_client.copy(
            table_id=table_id, to_storage_id=to_storage_id,
            collection_position=collection_position
        )
        for field in original_table["fields"]:
            field_copy, _ = await field_client.copy(
                field_id=field.get("_id"), table_id=table_copy, collection_position=collection_position
            )
            fields_copy.append(field_copy)

        for value in original_table["values"]:
            value_copy, _ = await value_client.copy(
                value_id=value.get("_id"), table_id=table_copy, collection_position=collection_position
            )
            values_copy.append(value_copy)

        await table_client.update(table_id=table_copy, data={"fields": fields_copy, "values": values_copy},
                                  collection_position=collection_position)
        return table_copy
