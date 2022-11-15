from api import fields, storage, tables, values, copy


fields_client = None
storage_client = None
table_client = None
value_client = None
copy_client = None


def client(base_url: str):
    global fields_client, storage_client, table_client, value_client, copy_client
    copy_client = copy.CopyClient(base_url=base_url)
    fields_client = fields.FieldsClient(base_url=base_url)
    storage_client = storage.StorageClient(base_url=base_url)
    table_client = tables.TableClient(base_url=base_url)
    value_client = values.ValuesClient(base_url=base_url)
