# coding=utf8

import json
import random
import logging
from hashlib import md5
from copy import deepcopy
from datetime import datetime
from collections import defaultdict

import redis
import gevent

from log import hit_logger
from risk_models.exceptions import RuleNotExistsException
from risk_models.strategy import Strategys
from clients import get_config_redis_client

logger = logging.getLogger(__name__)

strategys = Strategys()


class Rule(object):
    def __init__(self, d):
        self.id = d['id']
        self.uuid = d['uuid']
        self.name = d['title']
        self.strategy_group_list = []
        origin_strategy_group_list = json.loads(d['strategys'])
        for strategy_group in origin_strategy_group_list:
            weight = int(strategy_group['weight'])
            control = strategy_group['control']
            custom = strategy_group['custom']
            group_name = strategy_group['name']
            strategy_list = []
            origin_strategy_list = strategy_group['strategy_list']
            uuids = []
            for uuid_, threshold_list, _ in origin_strategy_list:
                uuids.append(uuid_)
                strategy_list.append([uuid_, threshold_list])
            group_uuid = self._build_group_uuid(uuids)
            self.strategy_group_list.append([strategy_list, control, custom,
                                             group_name, group_uuid, weight])

    def get_control_from_group_name(self, group_name):
        for _, c, _, g, _, _ in self.strategy_group_list:
            if g == group_name:
                return c

    def _build_group_uuid(self, uuids):
        uuid_str = ''.join(uuids)
        return md5(uuid_str.encode()).hexdigest()

    def get_callable_list(self):
        callable_list = []
        for (strategy_list, control, custom, group_name, group_uuid,
             weight) in self.strategy_group_list:
            funcs = []
            for uuid_, threshold_list in strategy_list:
                funcs.append(strategys.get_callable(uuid_, threshold_list))
            callable_list.append([funcs, control, custom, group_name,
                                  group_uuid, weight])
        return callable_list

    def __str__(self):
        return "{name}[id:{id}; uuid:{uuid}]".format(name=self.name,
                                                     id=self.id,
                                                     uuid=self.uuid)

    __repr__ = __str__


class Rules(object):
    def __init__(self, auto_refresh=False, load_all=False):
        self.load_all = load_all
        self.id_rule_map = {}
        strategys.load_strategys()
        self.load_rules()
        if auto_refresh:
            gevent.spawn(self.refresh)

    def _should_load(self, d):
        #  支持两种load方式：仅load开启状态且未过期的规则，load所有规则
        if self.load_all:
            return True
        status = d.get('status')
        try:
            end_time = datetime.strptime(d['end_time'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            logger.error('get invalid rule data %s', d)
            return False
        return status == 'on' and end_time > datetime.now()

    def load_rules(self):
        id_rule_map = {}
        conn = get_config_redis_client()
        logger.info('start load rules, current rule ids: %s',
                    self.id_rule_map.keys())
        try:
            for name in conn.scan_iter(match='rule:*'):
                d = conn.hgetall(name)
                if self._should_load(d):
                    rule = Rule(d)
                    id_rule_map[rule.id] = rule
        except redis.RedisError:
            logger.error('load rules occur redis conn error')
            return
        self.id_rule_map = id_rule_map
        logger.info('load rules success, current rule ids: %s',
                    self.id_rule_map.keys())

    def refresh(self):
        while True:
            gevent.sleep(300 + random.randint(1, 60))
            logger.info('start refresh strategys or rules')
            try:
                strategys.load_strategys()
                self.load_rules()
            except Exception as e:
                logger.error('refresh strategys or rules failed', exc_info=e)
            else:
                logger.info('refresh strategys or rules success')

    def get_callable_list(self, id_):
        rule = self.id_rule_map.get(id_)
        if not rule:
            raise RuleNotExistsException(
                'rule id({}) does not exists'.format(id_))
        return rule.get_callable_list()

    def _get_rule_or_raise(self, id_):
        rule = self.id_rule_map.get(id_)
        if not rule:
            raise RuleNotExistsException(
                'rule id ({}) does not exists'.format(id_))
        return rule

    def get_rule_name(self, id_):
        """根据id返回规则name"""
        rule = self._get_rule_or_raise(id_)
        return rule.name

    def get_all_rule_id_and_name(self):
        """返回所有规则的id和name映射关系"""
        return [(k, v.name) for k, v in self.id_rule_map.items()]

    def get_all_rule_uuid_and_name(self):
        """返回所有规则的uuid和name映射关系"""
        return [(v.uuid, v.name) for v in self.id_rule_map.values()]

    def get_all_group_uuid_and_name(self):
        """
        返回所有的策略原子组uuid和名称
        *因html中typeahead需要， 此处 group_uuid 前拼接了rule_id
        """
        data = []
        for d in self.id_rule_map.values():
            for (strategy_list, control, custom, group_name, group_uuid,
                 weight) in d.strategy_group_list:
                data.append(("{}_{}".format(d.id, group_uuid), group_name))
        return data

    def get_rule_control_name(self, rule_id, group_name):
        rule = self.id_rule_map[rule_id]
        return rule.get_control_from_group_name(group_name)


class AccessCount(object):
    def __init__(self, auto_persist=False):
        self.conn = get_config_redis_client()
        self.id_count_map = defaultdict(int)
        self.redis_hash_key_temp = 'access_count_{}'
        if auto_persist:
            gevent.spawn(self.auto_persist)

    def incr(self, id_):
        self.id_count_map[id_] += 1

    def persist(self):
        id_count_map = deepcopy(self.id_count_map)
        today = datetime.today()
        today_str = today.strftime('%Y%m%d')
        redis_hash_key = self.redis_hash_key_temp.format(today_str)
        try:
            for k, v in id_count_map.items():
                self.conn.hincrby(redis_hash_key, k, v)
        except redis.RedisError as e:
            logger.error('incr access_count failed', exc_info=e)
            return
        #  全部写入之后再进行扣减
        for k, v in id_count_map.items():
            self.id_count_map[k] -= v

    def auto_persist(self):
        while True:
            gevent.sleep(60 + random.randint(1, 5))
            try:
                self.persist()
            except Exception as e:
                logger.error('incr access_count failed', exc_info=e)


def calculate_rule(id_, req_body, rules=None, ac=None):
    if rules is None:
        #  调试时用
        rules = Rules()
    if ac:
        ac.incr(id_)
    else:
        #  此时是web页中访问的计数
        ac = AccessCount()
        ac.incr(id_)
        ac.persist()

    rv_control, rv_weight, result_seted, hit_number = 'pass', 0, False, 0

    for (funcs, control, custom, group_name, group_uuid,
         weight) in rules.get_callable_list(id_):
        results = []
        for func in funcs:
            try:
                ret = func(req_body)
            except Exception:
                logger.error(
                    'run func error, rule_id: {}, weight: {}'.format(id_,
                                                                     weight),
                    exc_info=True)
                ret = False
            results.append(ret)
            if not ret:
                break

        # 目前策略为过全部策略原子组以积累数据，若无此需求，可自行进行短路
        if all(results):
            if not result_seted:
                rv_control, rv_weight, result_seted = control, weight, True

            # 当前命中的策略组在此规则中是第几个命中的
            hit_number += 1

            msg = json.dumps(dict(rule_id=id_,
                                  kwargs={},
                                  req_body=req_body,
                                  control=control,
                                  custom=custom,
                                  group_name=group_name,
                                  group_uuid=group_uuid,
                                  hit_number=hit_number))
            hit_logger.info(msg)
    return rv_control, rv_weight
