# coding=utf-8

from core.utils import get_sample_str

from strategy.forms import (MenuStrategyForm, BoolStrategyForm,
                            UserStrategyForm, FreqStrategyForm)


def _create_new_strategy(form_cls, strategy_conf):
    form_obj = form_cls(data=strategy_conf)

    if form_obj.is_valid():
        # 创建成功
        new_strategy_uuid = form_obj.save()
        return True, new_strategy_uuid
    else:
        return False, ''


def create_menu_strategy(event, dimension, menu_type, menu_op,
                         strategy_name=None, strategy_desc=None):
    """
        新建名单型策略
    :param str|unicode event: 项目uuid
    :param str|unicode dimension: 维度  user_id / ip / uid ...
    :param str|unicode menu_type: 名单类型  black, white, gray
    :param str|unicode menu_op: 操作码 在/不在(is/is_not)
    :param str|unicode strategy_name: 策略名称
    :param str|unicode strategy_desc: 策略描述
    """

    strategy_name = strategy_name or get_sample_str()
    strategy_desc = strategy_desc or get_sample_str()

    data = {
        'strategy_name': strategy_name,
        'strategy_desc': strategy_desc,
        'menu_op': menu_op,
        'event': event,
        'dimension': dimension,
        'menu_type': menu_type
    }

    success, strategy_uuid = _create_new_strategy(
        MenuStrategyForm, strategy_conf=data
    )
    assert success, 'create menu strategy fail.'
    return strategy_uuid


def create_bool_strategy(strategy_var, strategy_op, strategy_func,
                         strategy_threshold, strategy_name=None,
                         strategy_desc=None):
    """
        新建bool型策略
    :param str|unicode strategy_var: 内置变量
    :param str|unicode strategy_op: 操作码
    :param str|unicode strategy_func: 内置函数
    :param str|unicode strategy_threshold: 策略的阈值
    :param str|unicode strategy_name: 策略名称
    :param str|unicode strategy_desc: 策略描述
    :return:
    """

    strategy_name = strategy_name or get_sample_str()
    strategy_desc = strategy_desc or get_sample_str()

    data = {
        'strategy_var': strategy_var,
        'strategy_op': strategy_op,
        'strategy_func': strategy_func,
        'strategy_threshold': strategy_threshold,
        'strategy_name': strategy_name,
        'strategy_desc': strategy_desc
    }

    success, strategy_uuid = _create_new_strategy(
        BoolStrategyForm, strategy_conf=data
    )
    assert success, 'create bool strategy fail.'
    return strategy_uuid


def create_user_strategy(strategy_source, strategy_body, strategy_day,
                         strategy_limit, strategy_name=None,
                         strategy_desc=None):
    """
        新建限用户数型策略
    :param str|unicode strategy_source: 上报数据源key
    :param str|unicode strategy_body: 限制主体 eg:  ip, uid, user_id  etc...
    :param int strategy_day: 自然天数
    :param int strategy_limit: 限制用户数
    :param str|unicode strategy_name: 策略名称
    :param str|unicode strategy_desc: 策略描述
    :return:
    """
    strategy_name = strategy_name or get_sample_str()
    strategy_desc = strategy_desc or get_sample_str()

    data = {
        'strategy_source': strategy_source,
        'strategy_body': strategy_body,
        'strategy_day': strategy_day,
        'strategy_limit': strategy_limit,
        'strategy_name': strategy_name,
        'strategy_desc': strategy_desc
    }

    success, strategy_uuid = _create_new_strategy(
        UserStrategyForm, strategy_conf=data
    )
    assert success, 'create bool strategy fail.'
    return strategy_uuid


def create_freq_strategy(strategy_source, strategy_body, strategy_time,
                         strategy_limit, strategy_name=None,
                         strategy_desc=None):
    """
        新建时段频控型策略
    :param str|unicode strategy_source: 上报数据源key
    :param str|unicode strategy_body: 限制主体 eg:  ip, uid, user_id  etc...
    :param int strategy_time: 时段(单位为秒)
    :param int strategy_limit: 限制个数
    :param request: 请求对象，需要从中取得用户信息等
    :param str|unicode strategy_name: 策略名称
    :param str|unicode strategy_desc: 策略描述
    :return:
    """
    strategy_name = strategy_name or get_sample_str()
    strategy_desc = strategy_desc or get_sample_str()

    data = {
        'strategy_source': strategy_source,
        'strategy_body': strategy_body,
        'strategy_time': strategy_time,
        'strategy_limit': strategy_limit,
        'strategy_name': strategy_name,
        'strategy_desc': strategy_desc
    }
    success, strategy_uuid = _create_new_strategy(FreqStrategyForm,
                                                  strategy_conf=data)
    assert success, 'create freq strategy fail.'
    return strategy_uuid
