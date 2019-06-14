# coding=utf-8
import json
from datetime import datetime, timedelta

from django.core.urlresolvers import reverse

from core.testcase import BaseTestCase
from core.utils import get_sample_str
from log_manage.init_data import create_hit_table


class TestHitListDetailCase(BaseTestCase):

    def test_hit_detail_view(self):
        url = reverse('log_manage:hit_list_detail')

        # 普通
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        # 带用户
        data = {
            'user_id': 11
        }
        response = self.client.get(url, data)
        self.assertEquals(response.status_code, 200)

        # 表不存在 & 带时间
        right = datetime.now()
        left = right - timedelta(days=1)
        data = {
            'user_id': 11,
            'start_day': left.strftime('%Y/%m/%d'),
            'end_day': right.strftime('%Y/%m/%d')
        }
        response = self.client.get(url, data=data)
        self.assertEquals(response.status_code, 200)

        # 表存在 & 带时间
        create_hit_table(left)
        response = self.client.get(url, data=data)
        self.assertEquals(response.status_code, 200)

        # 带错误的时间
        data = {
            'user_id': 11,
            'start_day': get_sample_str(8),
            'end_day': get_sample_str(8)
        }
        response = self.client.get(url, data=data)
        self.assertEquals(response.status_code, 200)


class TestRuleStrategyMapView(BaseTestCase):

    def test_view(self):
        url = reverse('log_manage:rule_strategy_map')

        # 参数不全
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        t = json.loads(response.content)

        self.assertEquals(t['state'], False)
        self.assertEquals(t['rules_num'], 0)

        # 全部
        for rule_id in {u'', u'所有'}:
            data = {'rule_id': rule_id}
            response = self.client.get(url, data)
            self.assertEquals(response.status_code, 200)
            t = json.loads(response.content)

            self.assertEquals(t['state'], True)
            self.assertEquals(t['strategy_groups'], {})

        # 规则不存在
        response = self.client.get(url, {'rule_id': 'no_exixts_rule_id'})
        self.assertEquals(response.status_code, 200)
        t = json.loads(response.content)

        self.assertEquals(t['state'], False)
        self.assertEquals(t['rules_num'], 0)

        # 存在规则
        # todo..


class TestAuditLogView(BaseTestCase):

    def test_view(self):
        url = reverse('log_manage:audit_logs')

        # 无参访问
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        # 正常时间
        right = datetime.now()
        left = right - timedelta(hours=1)
        data = {
            'time__gt': left.strftime('%Y-%m-%d %H:%M:%S'),
            'time__lt': right.strftime('%Y-%m-%d %H:%M:%S')
        }
        response = self.client.get(url, data=data)
        self.assertEquals(response.status_code, 200)

        # 少参访问
        data.pop('time__lt')
        response = self.client.get(url, data=data)
        self.assertEquals(response.status_code, 200)
