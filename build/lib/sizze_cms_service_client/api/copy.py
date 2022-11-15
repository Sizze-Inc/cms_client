from api.collection import CmsClient
from api import fields, storage, tables, values


class CopyClient(CmsClient):
    async def full_copy_storage(self, storage_id: str, to_project_id: int, users: list, collection_position: int = 1):
        storage_client = storage.StorageClient(base_url=self.base_url)
        table_client = tables.TableClient(base_url=self.base_url)

        original_storage = await storage_client.retrieve(storage_id=storage_id)
        original_tables = await table_client.list(storage_id=original_storage.get("_id"),
                                                  collection_position=collection_position)
        storage_copy = await storage_client.create(project_id=to_project_id, users=users,
                                                   index=original_storage.get("_id"))
        tables_copy = []
        for original_table in original_tables:
            table_copy = self.full_copy_table(table_id=original_table.get("_id"), to_storage_id=storage_copy,
                                              original_table=original_table, collection_position=collection_position)
            tables_copy.append(table_copy)
        await storage_client.update(storage_id=storage_copy, tables=tables_copy,
                                    collection_position=collection_position)

    async def full_copy_table(self, table_id: str, to_storage_id: str, original_table: dict = None,
                              collection_position: int = 1):
        table_client = tables.TableClient(base_url=self.base_url)
        value_client = values.ValuesClient(base_url=self.base_url)
        field_client = fields.FieldsClient(base_url=self.base_url)

        fields_copy = []
        values_copy = []
        if original_table is None:
            original_table = await table_client.retrieve(table_id=table_id)

        table_copy = await table_client.copy(table_id=table_id, to_storage_id=to_storage_id,
                                             collection_position=collection_position)
        for field in original_table["fields"]:
            field_copy = await field_client.copy(field_id=field.get("_id"), table_id=table_copy,
                                                 collection_position=collection_position)
            fields_copy.append(field_copy)

        for value in original_table["values"]:
            value_copy = await value_client.copy(value_id=value.get("_id"), table_id=table_copy,
                                                 collection_position=collection_position)
            values_copy.append(value_copy)

        await table_client.update(table_id=table_copy, fields=fields_copy, values=values_copy,
                                  collection_position=collection_position)
        return table_copy
