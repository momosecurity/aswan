# coding=utf-8
import copy
import json
from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from bk_config.init_data import create_data_source
from core.testcase import BaseTestCase
from core.utils import get_sample_str
from menu.init_data import create_menu_event, add_element_to_menu
from strategy.init_data import (create_menu_strategy, create_user_strategy,
                                create_bool_strategy, create_freq_strategy)


class TestRuleManage(BaseTestCase):
    list_url = 'rule:list'
    create_url = 'rule:create'
    destroy_url = 'rule:destroy'
    change_url = 'rule:change'
    detail_url = 'rule:detail'
    test_url = 'rule:test'
    data_url = 'rule:data'
    edit_url = 'rule:edit'
    edit_threshold_url = 'rule:threshold_edit'

    def setUp(self):
        super(TestRuleManage, self).setUp()
        self.request_factory = RequestFactory()

    def _test_list(self):
        list_url = reverse(self.list_url)

        # 无条件访问
        response = self.client.get(list_url)
        self.assertEquals(response.status_code, 200)

        # 带条件访问
        data = {
            'status': 'on',
            'rule_name': 'xx'
        }
        response = self.client.get(list_url, data=data)
        self.assertEquals(response.status_code, 200)

    def _test_create(self):
        create_url = reverse(self.create_url)

        # 初始页面
        response = self.client.get(create_url)
        self.assertEquals(response.status_code, 200)

        # 创建规则

        # 无参数
        response = self.client.post(create_url)
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEquals(resp_json['state'], False)

        # 正常创建
        event_code = create_menu_event()['event_code']
        add_element_to_menu(event_code=event_code, menu_type='black',
                            dimension='user_id', element='111111')

        # user_id 在 event_code 所代表的黑名单中
        self.menu_strategy_uuid = create_menu_strategy(event_code=event_code,
                                                       dimension='user_id',
                                                       menu_type='black',
                                                       menu_op='is')

        # 相同uid，当天限1个用户
        data_source_key = create_data_source()
        self.user_strategy_uuid = create_user_strategy(
            strategy_source=data_source_key, strategy_body='uid',
            strategy_day=1, strategy_limit=1)

        # 用户是异常用户
        self.bool_strategy_uuid = create_bool_strategy(strategy_var='user_id',
                                                       strategy_op='is',
                                                       strategy_func='is_abnormal',
                                                       strategy_threshold='')

        # 相同uid，在最近86400s内，限1次
        self.freq_strategy_uuid = create_freq_strategy(
            strategy_source=data_source_key, strategy_body='uid',
            strategy_time=24 * 60 * 60, strategy_limit=1)

        self.valid_post_data = {
            'title': get_sample_str(10),
            'describe': get_sample_str(8),
            'status': 'on',
            'end_time': (datetime.today() + timedelta(days=100)).strftime(
                '%Y-%m-%d %H:%M:%S'),
            'strategys': ','.join(
                [self.menu_strategy_uuid, self.user_strategy_uuid,
                 self.bool_strategy_uuid, self.freq_strategy_uuid]),
            'controls': ','.join(['deny', 'log', 'number', 'pass']),
            'customs': ':::'.join([get_sample_str()] * 4),
            'names': ':::'.join([get_sample_str()] * 4),
            'weights': ','.join(['100', '90', '80', '70'])
        }
        response = self.client.post(create_url, data=self.valid_post_data)
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEquals(resp_json['state'], True)
        self.rule_uuid = resp_json['uuid']

    def _test_change(self):
        change_url = reverse(self.change_url)

        valid_post_data = copy.deepcopy(self.valid_post_data)

        valid_post_data['id'] = self.rule_uuid

        # 正常请求
        a = [[self.menu_strategy_uuid, [], get_sample_str()]]
        b = [[self.user_strategy_uuid, ["10", "10"], get_sample_str()]]
        c = [[self.bool_strategy_uuid, [], get_sample_str()]]
        d = [[self.freq_strategy_uuid, ["86400", "1"], get_sample_str()]]

        valid_post_data['strategys'] = '|'.join(
            [json.dumps(t) for t in (a, b, c, d)])
        response = self.client.post(change_url, data=valid_post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)['state'], True)

        # 状态不合法
        status = valid_post_data.pop('status')
        valid_post_data['status'] = 'wrong_status'
        response = self.client.post(change_url, data=valid_post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)['state'], False)

        # 仅修改阈值
        valid_post_data['status'] = status
        end_time_str = valid_post_data.pop('end_time')
        response = self.client.post(change_url, data=valid_post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)['state'], True)

        # 时间格式不合法
        valid_post_data['end_time'] = 'xxxxx'
        response = self.client.post(change_url, data=valid_post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)['state'], False)

        # 无规则名
        valid_post_data['end_time'] = end_time_str
        title = valid_post_data.pop('title')
        response = self.client.post(change_url, data=valid_post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)['state'], False)

        # 无描述
        valid_post_data['title'] = title
        describe = valid_post_data.pop('describe')
        response = self.client.post(change_url, data=valid_post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)['state'], False)

        # 表格数据留空/长度不匹配
        valid_post_data['describe'] = describe
        names = valid_post_data.pop('names')
        response = self.client.post(change_url, data=valid_post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)['state'], False)

        # 策略数据错误
        valid_post_data['names'] = names
        strategys_str = valid_post_data.pop('strategys')
        valid_post_data['strategys'] = strategys_str[:-2]
        response = self.client.post(change_url, data=valid_post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)['state'], False)

        # 权重非数字
        valid_post_data['strategys'] = strategys_str
        weights = valid_post_data.pop('weights')
        valid_post_data['weights'] = weights + 'x'
        response = self.client.post(change_url, data=valid_post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)['state'], False)

    def _test_destroy(self):
        destroy_url = reverse(self.destroy_url)
        data = {}
        response = self.client.post(destroy_url, data=data)
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEquals(resp_json['state'], False)
        self.assertEquals(resp_json['error'], u'未找到规则')

        data['id'] = self.rule_uuid
        response = self.client.post(destroy_url, data=data)
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEquals(resp_json['state'], True)
        self.assertEquals(resp_json['msg'], 'ok')

    def _test_detail(self):
        detail_url = reverse(self.detail_url)

        # 请求不存在的规则详情页
        no_exists_id = 'no_exists_rule_uuid'
        response = self.client.get(detail_url, data={'id': no_exists_id})
        self.assertEquals(response.status_code, 404)

        # 正常的页面
        response = self.client.get(detail_url, data={'id': self.rule_uuid})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['rule']['uuid'], self.rule_uuid)

    def _test_test(self):
        test_url = reverse(self.test_url)

        # 测试页面
        response = self.client.get(test_url)
        self.assertEquals(response.status_code, 200)

        # 缺少参数
        response = self.client.post(test_url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)['state'], False)

        # 正常请求
        req_body = {
            'user_id': '111111',
            'uid': '111111'
        }
        response = self.client.post(test_url,
                                    data={'req_body': json.dumps(req_body),
                                          'rule': self.rule_uuid})
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEquals(resp_json['state'], True)
        self.assertEquals(resp_json['data'], u'拒绝')

        req_body['user_id'] = '222222'
        response = self.client.post(test_url,
                                    data={'req_body': json.dumps(req_body),
                                          'rule': self.rule_uuid})
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEquals(resp_json['state'], True)
        self.assertEquals(resp_json['data'], u'数字验证')

    def _test_edit(self):
        edit_url = reverse(self.edit_url)

        # 空参数
        response = self.client.get(edit_url)
        self.assertEquals(response.status_code, 404)

        # 不存在的key
        response = self.client.get(edit_url, {'id': 'no_exists_id'})
        self.assertEquals(response.status_code, 404)

        # 正常请求
        response = self.client.get(edit_url, data={'id': self.rule_uuid})
        self.assertEquals(response.status_code, 200)
        context = response.context
        self.assertEquals(context['rule']['uuid'], self.rule_uuid)

    def _test_threshold_edit(self):
        edit_threshold_url = reverse(self.edit_threshold_url)

        # 空参数
        response = self.client.post(edit_threshold_url)
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEquals(resp_json['state'], False)

        # 正常访问
        data = {
            "rule_uuid": self.rule_uuid,
            "strategy_index": 1,
            "strategy_list": [{
                "strategy_uuid": self.user_strategy_uuid,
                "threshold_list": ["10", "10"]
            }]
        }
        response = self.client.post(edit_threshold_url,
                                    data={'data': json.dumps(data)})
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEquals(resp_json['state'], True)

        # 数组下标越界
        data['strategy_index'] = 10000
        response = self.client.post(edit_threshold_url,
                                    data={'data': json.dumps(data)})
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEquals(resp_json['state'], False)

        # 不存在的uuid
        data['strategy_index'] = 1
        data['rule_uuid'] = 'no_exists_uuid'
        response = self.client.post(edit_threshold_url,
                                    data={'data': json.dumps(data)})
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEquals(resp_json['state'], False)

    def _test_data(self):
        data_url = reverse(self.data_url)

        # 无参调用
        response = self.client.post(data_url)
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEquals(resp_json['state'], False)

        # 不存在的uuid调用
        response = self.client.post(data_url, data={'uuid': 'no_exists_uuid'})
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEquals(resp_json['state'], False)

        # 正常请求
        response = self.client.post(data_url, data={'uuid': self.rule_uuid})
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEquals(resp_json['state'], True)

    def test_view(self):
        self._test_create()
        self._test_list()
        self._test_detail()
        self._test_edit()
        self._test_threshold_edit()
        self._test_test()
        self._test_change()
        self._test_data()
        self._test_destroy()
