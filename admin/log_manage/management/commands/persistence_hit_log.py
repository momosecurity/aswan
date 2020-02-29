# coding=utf8

import time
import json
import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import connection

from config import HIT_LOG_QUEUE_NAME
from clients import get_log_redis_client
from log_manage.models import get_hit_log_model

logger = logging.getLogger(__name__)

table_cls_map = {}


def get_private_queue_name():
    """
        # 本进程持有的私有队列key, 若需扩展，需重写生成方式
    """
    return HIT_LOG_QUEUE_NAME + '_tmp'


def parse_msg(msg):
    dt, body = msg.split('|', 1)
    dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S,%f')
    d = json.loads(body)
    d['time'] = dt
    req_body = d['req_body']
    d['user_id'] = req_body.get('user_id', '')
    d['req_body'] = json.dumps(req_body, ensure_ascii=False)
    return d


def table_exists(table_name):
    with connection.cursor() as cursor:  # 判断数据表是否存在
        all_table_names = set(
            connection.introspection.table_names(cursor=cursor))
    return table_name in all_table_names


def get_or_create_model_cls(table_name):
    try:
        return table_cls_map[table_name]
    except KeyError:
        pass

    model_cls = get_hit_log_model(table_name)
    if not table_exists(table_name):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(model_cls)
    table_cls_map[table_name] = model_cls
    return model_cls


def persistence_data(data):
    dt = data['time']
    table_name = 'hit_log_{}'.format(dt.strftime('%Y%m%d'))

    model_cls = get_or_create_model_cls(table_name)

    value_map = {}
    for key in ['time', 'rule_id', 'user_id', 'kwargs',
                'req_body', 'control', 'custom', 'group_name', 'group_uuid',
                'hit_number']:
        value_map[key] = data.get(key)

    # todo batch
    model_cls.objects.create(**value_map)


def process_hit_log_msg(msg):
    try:
        data = parse_msg(msg)
    except Exception:
        logger.error('invalid msg: {msg}'.format(msg=msg))
        return
    try:
        persistence_data(data)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        logger.error('persistence data error: {msg}'.format(msg=msg))


def main(conn, private_queue_name):
    while True:
        sp_log = conn.lindex(private_queue_name, -1)

        if not sp_log:
            sp_log = conn.rpoplpush(HIT_LOG_QUEUE_NAME,
                                    private_queue_name)

        if sp_log:
            process_hit_log_msg(sp_log)
            conn.lpop(private_queue_name)
        else:
            time.sleep(0.1)


class Command(BaseCommand):
    def handle(self, *args, **options):
        redis_client = get_log_redis_client()
        private_queue_name = get_private_queue_name()
        while True:
            try:
                main(redis_client, private_queue_name)
            except Exception:
                logger.exception('hit log persistence have error')
                time.sleep(0.1)
