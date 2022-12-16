from sizze_cms_service_client.api import fields, storage, tables, values, copy, user


fields_client = fields.FieldsClient()
storage_client = storage.StorageClient()
table_client = tables.TableClient()
value_client = values.ValuesClient()
copy_client = copy.CopyClient()
user_client = user.UserClient()


def client(base_url: str):
    global fields_client, storage_client, table_client, value_client, copy_client
    copy_client.set_base_url(base_url)
    fields_client.set_base_url(base_url)
    storage_client.set_base_url(base_url)
    table_client.set_base_url(base_url)
    value_client.set_base_url(base_url)
    user_client.set_base_url(base_url)
