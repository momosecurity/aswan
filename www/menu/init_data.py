# coding=utf-8

import uuid
from datetime import datetime, timedelta

from www.core.pymongo_client import get_mongo_client
from www.core.redis_client import get_redis_client
from www.core.utils import get_sample_str
from risk_models.menu import build_redis_key


def create_menu_event(event_code=None, event_name=None):
    db = get_mongo_client()
    payload = dict(
        event_code=event_code or str(uuid.uuid4()),
        event_name=event_name or get_sample_str(length=8)
    )
    db['menu_event'].insert_one(payload)
    return payload


def add_element_to_menu(event_code, menu_type, dimension, element,
                        end_time=None, menu_desc=None):
    """
        为名单中增加元素
    :param str|unicode event_code: 名单项目code
    :param str|unicode menu_type: 名单类型  black white gray
    :param str|unicode dimension: 名单维度 user_id / ip / ...
    :param str|unicode element: 放入名单的元素
    :param datetime end_time: 失效时间
    :param str|unicode menu_desc: 备注
    :return:
    """
    end_time = (end_time or datetime.now() + timedelta(hours=1))
    menu_desc = menu_desc or get_sample_str(15)
    payload = dict(
        end_time=end_time,
        menu_desc=menu_desc,
        menu_status=u"有效",
        create_time=datetime.now(),
        creator='test',
        value=element,
        event_code=event_code,
        dimension=dimension,
        menu_type=menu_type
    )
    db = get_mongo_client()
    insert_result = db['menus'].insert_one(payload)

    redis_client = get_redis_client()
    redis_key = build_redis_key(event_code, dimension=dimension,
                                menu_type=menu_type)
    if redis_key:
        redis_client.sadd(redis_key, element)

    return str(insert_result.inserted_id)
