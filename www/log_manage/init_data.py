from django.db import connection

from log_manage.models import get_hit_log_model


def create_hit_table(date_obj):
    table_name = 'hit_log_{}'.format(date_obj.strftime('%Y%m%d'))

    model_cls = get_hit_log_model(db_table=table_name)
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(model_cls)
