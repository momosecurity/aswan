# coding=utf-8

import logging

from risk_models.cache import menu_cache

logger = logging.getLogger(__name__)
logging.basicConfig()


def build_redis_key(event_code: str, dimension: str, menu_type: str):
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


def get_element(req_body: dict, dimension: str) -> str:
    """ 从req_body中得到所需维度的数据 """
    # 目前全部从业务传参中获取
    return req_body.get(dimension, '')


def convert_dimension(dimension: str) -> str:
    """ 将配置中的某个key映射到某个名单维度 """

    # 暂时写死，之后可以配置化
    convert_map = {
        "reg_ip": "ip",
        "reg_uid": "uid"
    }
    return convert_map.get(dimension, dimension)


def hit_menu(req_body, op_name, event, dimension, menu_type):
    element = get_element(req_body, dimension)

    if not element:
        logger.warning(f'req_body({req_body}) does not contain {dimension}')
        return False

    dimension = convert_dimension(dimension)
    redis_key = build_redis_key(event, dimension, menu_type)

    if not redis_key:
        return False

    rv = element in menu_cache[redis_key]
    if op_name == 'is_not':
        rv = not rv

    return rv
