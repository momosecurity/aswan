# coding=utf-8

import logging

from risk_models.cache import menu_cache

logger = logging.getLogger(__name__)


def build_redis_key(event_code, dimension, menu_type):
    """
    :param event_code: 名单code
    :param dimension:  名单维度
    :param menu_type:  名单类型 黑/白/灰
    :return:
    """
    fields = ['menu', event_code, dimension, menu_type]
    if all(fields):
        return ':'.join(fields)
    else:
        return ''


def hit_menu(req_body, op_name, event, dimension, menu_type):
    if dimension not in req_body:
        logger.error('req_body(%s) does not contain %s', req_body, dimension)
        return False

    redis_key = build_redis_key(event, dimension, menu_type)

    if not redis_key:
        return False

    rv = req_body[dimension] in menu_cache[redis_key]
    if op_name == 'is_not':
        rv = not rv

    return rv
