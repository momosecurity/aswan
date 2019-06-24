# coding=utf8

"""
    本脚本用于在用户不熟悉时预注数据
"""

import logging
import hashlib

from django.core.management.base import BaseCommand

from permissions.init_data import create_user
from menu.init_data import create_menu_event, add_element_to_menu
from bk_config.init_data import create_data_source
from strategy.init_data import (create_menu_strategy, create_bool_strategy,
                                create_freq_strategy, create_user_strategy)
from rule.init_data import create_rule

logger = logging.getLogger(__name__)
logging.basicConfig()


class Command(BaseCommand):
    def handle(self, *args, **options):
        # 创建普通用户
        create_user(email='momo_init@immomo.com', username='momo_init',
                    password='momo_init', is_superuser=False)

        # 创建名单
        event_code = 'init_event'
        create_menu_event(event_code=event_code, event_name='初始项目')
        add_element_to_menu(event_code, menu_type='black', dimension='user_id',
                            element='111111')
        add_element_to_menu(event_code, menu_type='white', dimension='uid',
                            element=hashlib.md5('white_uid'.encode()).hexdigest())
        add_element_to_menu(event_code, menu_type='gray', dimension='ip',
                            element='1.1.1.1')
        add_element_to_menu(event_code, menu_type='black', dimension='phone',
                            element=hashlib.md5('12345678901'.encode()).hexdigest())
        add_element_to_menu(event_code, menu_type='black', dimension='pay',
                            element=hashlib.md5('pay_account'.encode()).hexdigest())

        # 创建策略
        # 名单型策略
        menu_strategy_name_1 = '用户在初始项目的用户黑名单中'
        menu_uuid_1 = create_menu_strategy(event_code, dimension='user_id',
                                           menu_type='black', menu_op='is',
                                           strategy_name=menu_strategy_name_1,
                                           strategy_desc='初始黑名单策略')
        menu_strategy_name_2 = 'uid在初始项目的设备白名单中'
        menu_uuid_2 = create_menu_strategy(event_code, dimension='uid',
                                           menu_type='white', menu_op='is',
                                           strategy_name=menu_strategy_name_2,
                                           strategy_desc='初始白名单策略')
        menu_strategy_name_3 = 'IP在初始项目的IP灰名单中'
        menu_uuid_3 = create_menu_strategy(event_code, dimension='ip',
                                           menu_type='gray', menu_op='is',
                                           strategy_name=menu_strategy_name_3,
                                           strategy_desc='初始灰名单策略')

        # Bool型策略
        bool_strategy_name_1 = '用户是异常用户'
        bool_uuid_1 = create_bool_strategy(strategy_var='user_id',
                                           strategy_op='is',
                                           strategy_func='is_abnormal',
                                           strategy_threshold='',
                                           strategy_name=bool_strategy_name_1,
                                           strategy_desc=bool_strategy_name_1)
        bool_strategy_name_2 = '用户登录次数大于50次'
        bool_uuid_2 = create_bool_strategy(strategy_var='user_id',
                                           strategy_op='gt',
                                           strategy_func='user_login_count',
                                           strategy_threshold='50',
                                           strategy_name=bool_strategy_name_2,
                                           strategy_desc=bool_strategy_name_2)
        # 数据源相关策略
        # 创建数据源
        source_key = 'init_source_key'
        create_data_source(source_key=source_key, source_name='初始样例数据源',
                           fields=['user_id', 'uid', 'ip', 'phone'])

        # 时段频控型策略
        freq_strategy_name = '相同uid，24小时内限10次(初始样例数据源)'
        freq_uuid = create_freq_strategy(strategy_source=source_key,
                                         strategy_body='uid',
                                         strategy_time=24 * 3600,
                                         strategy_limit=10,
                                         strategy_name=freq_strategy_name,
                                         strategy_desc='初始时段频控型策略')
        # 限用户数型策略
        user_strategy_name = '同一设备当天内限10个用户(初始样例数据源)'
        user_uuid = create_user_strategy(strategy_source=source_key,
                                         strategy_body='uid',
                                         strategy_day=1, strategy_limit=10,
                                         strategy_name=user_strategy_name,
                                         strategy_desc='初始时段频控型策略')

        # 规则相关
        strategy_confs = [
            [';'.join((menu_strategy_name_1, menu_strategy_name_2,
                       menu_strategy_name_3)),
             ';'.join((menu_uuid_1, menu_uuid_2, menu_uuid_3)), 'deny',
             '此用户命中了名单型策略',
             '100'],
            [';'.join((bool_strategy_name_1, bool_strategy_name_2)),
             ';'.join((bool_uuid_1, bool_uuid_2)), 'log',
             '此用户命中了布尔型策略',
             '90'],
            [freq_strategy_name,
             freq_uuid, 'number',
             '此用户命中了时段频控型策略',
             '80'],
            [user_strategy_name,
             user_uuid, 'verify',
             '此用户命中了限用户数型策略',
             '80'],
        ]
        create_rule(strategy_confs=strategy_confs, title='初始规则',
                    describe='初始样例规则', status='on', creator_name='超级管理员')
