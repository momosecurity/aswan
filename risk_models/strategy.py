# coding=utf8

import re
import time
import math
import logging
from datetime import datetime
from functools import partial, wraps
from collections import defaultdict

import redis

from risk_models.menu import hit_menu
from builtin_funcs import BuiltInFuncs
from risk_models.source import FreqSource, UserSource
from clients import get_report_redis_client, get_config_redis_client

logger = logging.getLogger(__name__)


def partial_bind_uuid(f):
    @wraps(f)
    def inner(self, *args, **kwargs):
        partial_obj = f(self, *args, **kwargs)
        partial_obj.uuid = self.uuid
        partial_obj.name = self.name
        return partial_obj

    return inner


_used_strategies = set()


def register_strategy(cls):
    _used_strategies.add(cls)
    return cls


class Strategy(object):
    """策略原子基类"""

    def __init__(self, d):
        #  策略原子uuid
        self.uuid = d['uuid']
        #  策略原子名称
        self.name = d['strategy_name']
        # 调用计数
        self.query_count = 0

    def get_thresholds(self):
        """每种策略原子都必定有阈值列表,规则中的策略原子默认绑定此阈值
        此处返回的阈值列表其实是个字符串列表，并未进行类型转换"""
        raise NotImplementedError("must be writen by subclass")

    def build_strategy_name_from_thresholds(self, thresholds):
        """每种策略原子都必需能从阈值列表重新构造策略原子名"""
        raise NotImplementedError("must be writen by subclass")

    def get_callable(self):
        raise NotImplementedError("must be writen by subclass")

    def get_callable_from_threshold_list(self, threshold_list):
        """此方法根据给定阈值列表返回一个callable对象，
        该callable对象接受一个req_body作为输入，输出一个布尔值 和一个自定义字符串"""
        raise NotImplementedError("must be writen by subclass")

    def __str__(self):
        return "{}[{}]".format(self.name, self.uuid)

    def __repr__(self):
        return self.__str__()


@register_strategy
class BoolStrategy(Strategy):
    """ Bool型 """
    prefix = 'bool_strategy:*'

    def __init__(self, d):
        super(BoolStrategy, self).__init__(d)
        self.func_name = d['strategy_func']
        self.op_name = d['strategy_op']
        self.threshold = d['strategy_threshold']
        self.strategy_var = d['strategy_var']

    def get_thresholds(self):
        if not self.threshold:
            return []
        else:
            return [self.threshold]

    def build_strategy_name_from_thresholds(self, thresholds):
        if len(thresholds) == 1:
            threshold = str(thresholds[0])
            return re.sub(r'[\d.]+$', threshold, self.name)
        else:
            return self.name

    def get_callable(self):
        threshold = self.threshold or None
        return partial(BuiltInFuncs.run, builtin_func_name=self.func_name,
                       op_name=self.op_name, threshold=threshold)

    @partial_bind_uuid
    def get_callable_from_threshold_list(self, threshold_list):
        if not threshold_list:
            threshold = None
        else:
            threshold = threshold_list[0]
        return partial(BuiltInFuncs.run, builtin_func_name=self.func_name,
                       op_name=self.op_name, threshold=threshold)


@register_strategy
class FreqStrategy(Strategy):
    """ 时段频控型 """
    prefix = 'freq_strategy:*'
    conn = get_report_redis_client()
    source_cls = FreqSource

    def __init__(self, d):
        super(FreqStrategy, self).__init__(d)
        self.threshold = d['strategy_limit']
        self.second_count = d['strategy_time']

        name = d['strategy_source']
        keys = [x.strip() for x in d['strategy_body'].split(',')]
        self.source = self.source_cls(name, keys)

    def get_thresholds(self):
        return [self.second_count, self.threshold]

    def build_strategy_name_from_thresholds(self, thresholds):
        strategy_time, threshold = thresholds
        tmp_str = re.sub(r'[\d]+s', strategy_time + 's', self.name)
        return re.sub(r'[\d]+次', threshold, tmp_str)

    def get_callable(self):
        return self.query_with_history

    def _build_key_member_score_map(self, history_data):
        key_member_score_map = defaultdict(list)
        for data in history_data:
            keys, member, score = self.source.get_all(data)
            for key in keys:
                key_member_score_map[key].append((member, score))
        return key_member_score_map

    def query_with_history(self, req_body, history_data):
        zkeys = self.source.get_zkeys(req_body)
        #  获取不到内置变量，默认放过
        if not zkeys:
            return False

        second_count = int(self.second_count)
        start = time.time() - second_count
        threshold = int(self.threshold)
        key_member_score_map = self._build_key_member_score_map(history_data)

        for zkey in zkeys:
            count = 0
            for (member, score) in key_member_score_map[zkey]:
                if int(score) >= start:
                    count += 1
            if count >= threshold:
                return True
        return False

    def query(self, req_body, threshold, second_count):
        self.query_count += 1
        #  若请求不合法，则默认放过
        if not self.source.check_key(req_body):
            logger.error('invalid req_body(%s)', req_body)
            return False

        zkeys = self.source.get_zkeys(req_body)
        #  获取不到内置变量，默认放过
        if not zkeys:
            return False

        end = time.time()
        start = end - second_count

        for zkey in zkeys:
            count = 0
            #  计数
            try:
                count = self.conn.zcount(zkey, start, end) or 0
            except redis.RedisError:
                logger.error('zcount({}, {}, {}) failed'.format(zkey,
                                                                start, end))

            #  返回最终判断结果,任意命中即返回命中
            if count >= threshold:
                return True

        #  所有都不命中，返回不命中
        return False

    @partial_bind_uuid
    def get_callable_from_threshold_list(self, threshold_list):
        second_count, threshold = threshold_list
        second_count, threshold = int(second_count), int(threshold)
        return partial(self.query, threshold=threshold,
                       second_count=second_count)


@register_strategy
class MenuStrategy(Strategy):
    """ 名单型 """
    prefix = 'strategy_menu:*'

    def __init__(self, d):
        super(MenuStrategy, self).__init__(d)
        self.op_name = d['menu_op']
        self.event = d['event']
        self.dimension = d['dimension']
        self.menu_type = d['menu_type']

    def get_thresholds(self):
        return []

    def get_callable(self):
        return self.get_callable_from_threshold_list()

    def build_strategy_name_from_thresholds(self, thresholds):
        return self.name

    @partial_bind_uuid
    def get_callable_from_threshold_list(self, *args):
        return partial(hit_menu,
                       op_name=self.op_name,
                       event=self.event,
                       dimension=self.dimension,
                       menu_type=self.menu_type)


@register_strategy
class UserStrategy(Strategy):
    """ 限用户数型 """
    prefix = 'user_strategy:*'
    conn = get_report_redis_client()
    source_cls = UserSource

    def __init__(self, d):
        super(UserStrategy, self).__init__(d)
        self.threshold = d['strategy_limit']
        self.daily_count = d['strategy_day']

        name = d['strategy_source']
        keys = [x.strip() for x in d['strategy_body'].split(',')]
        self.source = self.source_cls(name, keys)

    def get_thresholds(self):
        return [self.daily_count, self.threshold]

    def build_strategy_name_from_thresholds(self, thresholds):
        strategy_day, threshold = thresholds
        tmp_str = self.name
        if "当天" in self.name:
            if int(strategy_day) > 1:
                tmp_str = re.sub(r"当天", strategy_day + "个自然日",
                                 self.name)
        else:
            if strategy_day == "1":
                tmp_str = re.sub(r'[\d]+个自然日', '当天', self.name)
            else:
                tmp_str = re.sub(r'[\d]+个自然日', strategy_day + '个自然日',
                                 self.name)
        return re.sub(r'[\d]+个用户', threshold + '个用户', tmp_str)

    def get_callable(self):
        return self.query_with_history

    def _build_key_member_score_map(self, history_data):
        key_member_score_map = defaultdict(list)
        for data in history_data:
            keys, member, score = self.source.get_all(data)
            for key in keys:
                key_member_score_map[key].append((member, score))
        return key_member_score_map

    def query_with_history(self, req_body, history_data):
        zkeys = self.source.get_zkeys(req_body)
        #  获取不到内置变量，默认放过
        if not zkeys:
            return False

        daily_count = int(self.daily_count)
        now = datetime.now()
        seconds = (daily_count - 1) * 86400 + now.hour * 3600 + now.minute * 60 + now.second
        start = time.time() - seconds
        threshold = int(self.threshold)
        key_member_score_map = self._build_key_member_score_map(history_data)

        for zkey in zkeys:
            hit_users = set()
            for (member, score) in key_member_score_map[zkey]:
                if int(score) >= start:
                    user_id = member.split(':', 1)[0]
                    hit_users.add(user_id)
            hit_users.discard(req_body['user_id'])
            if len(hit_users) >= threshold:
                return True
        return False

    def query(self, req_body, threshold, daily_count):
        self.query_count += 1
        #  若请求不合法，则默认放过
        if not self.source.check_key(req_body):
            logger.error('invalid req_body(%s)', req_body)
            return False

        zkeys = self.source.get_zkeys(req_body)
        if not zkeys:
            return False

        cur_time = datetime.now()
        seconds = (daily_count - 1) * 86400 + cur_time.hour * 3600 + cur_time.minute * 60 + cur_time.second
        end = time.time()
        start = math.floor(end - seconds)
        for zkey in zkeys:
            count = 0
            #  计数
            try:
                records = self.conn.zrangebyscore(zkey, start, end) or []
                hit_users = {x.split(':', 1)[0] for x in records}
                hit_users.discard(req_body['user_id'])
                count = len(hit_users)
            except redis.RedisError:
                logger.error('zrangebyscore({}, {}, {}) failed'.format(zkey,
                                                                       start,
                                                                       end))

            if count >= threshold:
                return True
        return False

    @partial_bind_uuid
    def get_callable_from_threshold_list(self, threshold_list):
        daily_count, threshold = threshold_list
        daily_count, threshold = int(daily_count), int(threshold)
        return partial(self.query, daily_count=daily_count,
                       threshold=threshold)


class Strategys(object):
    def __init__(self):
        self.uuid_strategy_map = {}
        self.load_strategys()

    def load_strategys(self):
        uuid_strategy_map = {}
        conn = get_config_redis_client()
        logger.info('start load strategys from db, current strategy: %s',
                    self.uuid_strategy_map.keys())
        for strategy_cls in _used_strategies:
            try:
                for name in conn.scan_iter(match=strategy_cls.prefix):
                    d = conn.hgetall(name)
                    strategy = strategy_cls(d)
                    uuid_strategy_map[strategy.uuid] = strategy
            except redis.RedisError:
                logger.error('load strategys occur redis conn error')
                return
        self.uuid_strategy_map = uuid_strategy_map
        logger.info('load strategys success, current strategy: %s',
                    self.uuid_strategy_map.keys())

    def _get_strategy_or_raise(self, uuid_):
        strategy = self.uuid_strategy_map.get(uuid_)
        if not strategy:
            raise ValueError('uuid({}) is not a valid strategy uuid'.format(uuid_))
        return strategy

    def get_thresholds(self, uuid_):
        strategy = self._get_strategy_or_raise(uuid_)
        return strategy.get_thresholds()

    def get_all_strategy_uuid_and_name(self):
        return [(uuid_, strategy.name) for (uuid_, strategy)
                in self.uuid_strategy_map.items()]

    def get_strategy_name(self, uuid_):
        strategy = self._get_strategy_or_raise(uuid_)
        return strategy.name

    def build_strategy_name_from_thresholds(self, uuid_, thresholds):
        strategy = self._get_strategy_or_raise(uuid_)
        return strategy.build_strategy_name_from_thresholds(thresholds)

    def get_callable(self, uuid_, threshold_list):
        strategy = self._get_strategy_or_raise(uuid_)
        return strategy.get_callable_from_threshold_list(threshold_list)
