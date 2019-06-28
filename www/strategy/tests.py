# coding=utf-8
import random
import time
import json

from django.core.urlresolvers import reverse

from bk_config.init_data import create_data_source
from core.utils import get_sample_str
from menu.init_data import create_menu_event, add_element_to_menu

from core.testcase import BaseTestCase


class TestStrategyViewMinix(object):
    list_uri = ''
    create_uri = ''
    destroy_uri = ''
    data_uri = ''
    test_uri = ''

    def _test_list(self):
        response = self.client.get(reverse(self.list_uri))
        self.assertEquals(response.status_code, 200)

    def _test_data(self):
        response = self.client.post(reverse(self.data_uri),
                                    data={'uuid': self.strategy_uuid})
        self.assertEquals(response.status_code, 200)

    def _test_create(self):
        pass

    def _test_destroy(self):
        req_body = {'id': self.strategy_uuid}
        response = self.client.post(reverse(self.destroy_uri), data=req_body)
        self.assertEquals(response.status_code, 200)

    def _test_test(self):
        pass

    def test_methods(self):
        self._test_create()
        self._test_data()
        self._test_list()
        self._test_test()
        self._test_destroy()


class TestMenuStrategyView(BaseTestCase, TestStrategyViewMinix):
    list_uri = 'strategy:menu_strategy_list'
    create_uri = 'strategy:menu_strategy_create'
    destroy_uri = 'strategy:menu_strategy_destroy'
    data_uri = 'strategy:menu_strategy_data'
    test_uri = 'strategy:menu_strategy_test'

    def _test_create(self):
        event_conf = create_menu_event()
        self.event_code = event_conf['event_code']
        req_body = {
            "dimension": "ip",
            "menu_op": "is",
            "event": self.event_code,
            "menu_type": "black",
            'strategy_name': 'test_strategy_name'
        }
        response = self.client.post(reverse(self.create_uri), data=req_body)
        self.assertEquals(response.status_code, 200)
        resp_dict = json.loads(response.content)

        self.strategy_uuid = resp_dict['uuid']
        self.assertIs(resp_dict['state'], True)

    def _test_test(self):
        super(TestMenuStrategyView, self)._test_test()

        sp_ip = '1.1.1.1'
        data = {
            'req_body': json.dumps({'ip': sp_ip}),
            'strategy': self.strategy_uuid
        }
        response = self.client.post(reverse(self.test_uri), data=data)
        self.assertEquals(response.status_code, 200)
        resp_dict = json.loads(response.content)
        self.assertIs(resp_dict['state'], True)
        self.assertEquals(resp_dict['data'], u'不命中')

        add_element_to_menu(event_code=self.event_code, element=sp_ip,
                            menu_type='black', dimension='ip')

        response = self.client.post(reverse(self.test_uri), data=data)
        self.assertEquals(response.status_code, 200)
        resp_dict = json.loads(response.content)
        self.assertIs(resp_dict['state'], True)
        self.assertEquals(resp_dict['data'], u'命中')


class TestBoolStrategyView(BaseTestCase, TestStrategyViewMinix):
    list_uri = 'strategy:bool_strategy_list'
    create_uri = 'strategy:bool_strategy_create'
    destroy_uri = 'strategy:bool_strategy_destroy'
    data_uri = 'strategy:bool_strategy_data'
    test_uri = 'strategy:bool_strategy_test'

    def _test_create(self):
        data = {
            'strategy_name': 'test_strategy_name',
            'strategy_desc': 'test_strategy_desc',
            'strategy_var': 'user_id',
            'strategy_op': 'is',
            'strategy_func': 'is_abnormal',
            'strategy_threshold': ''
        }
        response = self.client.post(reverse(self.create_uri), data=data)
        self.assertEquals(response.status_code, 200)
        resp_dict = json.loads(response.content)
        self.strategy_uuid = resp_dict['uuid']
        self.assertIs(resp_dict['state'], True)

    def _test_test(self):
        super(TestBoolStrategyView, self)._test_test()

        base_user_id = '111111'

        # 直接放过的情况
        data = {
            'req_body': json.dumps({'user_id': base_user_id + '0'}),
            'strategy': self.strategy_uuid
        }
        response = self.client.post(reverse(self.test_uri), data=data)
        self.assertEquals(response.status_code, 200)
        resp_dict = json.loads(response.content)
        self.assertIs(resp_dict['state'], True)
        self.assertEquals(resp_dict['data'], u'不命中')

        # 命中的情况
        data = {
            'req_body': json.dumps({'user_id': base_user_id + '1'}),
            'strategy': self.strategy_uuid
        }
        response = self.client.post(reverse(self.test_uri), data=data)
        self.assertEquals(response.status_code, 200)
        resp_dict = json.loads(response.content)
        self.assertIs(resp_dict['state'], True)
        self.assertEquals(resp_dict['data'], u'命中')

        # 不命中的情况
        data = {
            'req_body': json.dumps({'user_id': base_user_id + '5'}),
            'strategy': self.strategy_uuid
        }
        response = self.client.post(reverse(self.test_uri), data=data)
        self.assertEquals(response.status_code, 200)
        resp_dict = json.loads(response.content)
        self.assertIs(resp_dict['state'], True)
        self.assertEquals(resp_dict['data'], u'不命中')


class TestFreqStrategyView(BaseTestCase, TestStrategyViewMinix):
    list_uri = 'strategy:freq_strategy_list'
    create_uri = 'strategy:freq_strategy_create'
    destroy_uri = 'strategy:freq_strategy_destroy'
    data_uri = 'strategy:freq_strategy_data'
    test_uri = 'strategy:freq_strategy_test'

    def _test_create(self):
        source_key = create_data_source()
        data = {
            'strategy_source': source_key,
            'strategy_desc': get_sample_str(8),
            'strategy_body': 'uid',
            'strategy_name': get_sample_str(8),
            'strategy_time': random.randint(1000, 10000),
            'strategy_limit': random.randint(1, 3)
        }
        response = self.client.post(reverse(self.create_uri), data=data)
        self.assertEquals(response.status_code, 200)
        resp_dict = json.loads(response.content)
        self.strategy_uuid = resp_dict['uuid']
        self.assertIs(resp_dict['state'], True)

    def _test_test(self):
        super(TestFreqStrategyView, self)._test_test()
        history_data = [{'uid': '111',
                         'timestamp': int(time.time() - random.randint(1, 100))}
                        for _ in range(4)]

        # 命中
        data = {
            'req_body': json.dumps(
                {'uid': '111', 'timestamp': int(time.time())}),
            'strategy': self.strategy_uuid,
            'history_data': json.dumps(history_data)
        }
        response = self.client.post(reverse(self.test_uri), data=data)
        self.assertEquals(response.status_code, 200)
        resp_dict = json.loads(response.content)
        self.assertIs(resp_dict['state'], True)
        self.assertEquals(resp_dict['data'], u'命中')

        # 不命中
        data['history_data'] = ''
        response = self.client.post(reverse(self.test_uri), data=data)
        self.assertEquals(response.status_code, 200)
        resp_dict = json.loads(response.content)
        self.assertIs(resp_dict['state'], True)
        self.assertEquals(resp_dict['data'], u'不命中')


class TestUserStrategyView(BaseTestCase, TestStrategyViewMinix):
    list_uri = 'strategy:user_strategy_list'
    create_uri = 'strategy:user_strategy_create'
    destroy_uri = 'strategy:user_strategy_destroy'
    data_uri = 'strategy:user_strategy_data'
    test_uri = 'strategy:user_strategy_test'

    def _test_create(self):
        # 同uid下在...天内限1个
        source_key = create_data_source()
        data = {
            'strategy_source': source_key,
            'strategy_desc': get_sample_str(8),
            'strategy_body': 'uid',
            'strategy_name': get_sample_str(8),
            'strategy_day': random.randint(1, 10),
            'strategy_limit': 1
        }
        response = self.client.post(reverse(self.create_uri), data=data)
        self.assertEquals(response.status_code, 200)
        resp_dict = json.loads(response.content)
        self.strategy_uuid = resp_dict['uuid']
        self.assertIs(resp_dict['state'], True)

    def _test_test(self):
        super(TestUserStrategyView, self)._test_test()

        history_data = [{
            'uid': '111', 'user_id': '111',
            'timestamp': int(
                time.time() - random.randint(1, 100))
        }
            for _ in range(4)]

        # 命中
        data = {
            'req_body': json.dumps(
                {'uid': '111', 'user_id': '222',
                 'timestamp': int(time.time()) - 1}),
            'strategy': self.strategy_uuid,
            'history_data': json.dumps(history_data)
        }
        response = self.client.post(reverse(self.test_uri), data=data)
        self.assertEquals(response.status_code, 200)
        resp_dict = json.loads(response.content)
        self.assertIs(resp_dict['state'], True)
        self.assertEquals(resp_dict['data'], u'命中')

        # 不命中
        data['history_data'] = ''

        response = self.client.post(reverse(self.test_uri), data=data)
        self.assertEquals(response.status_code, 200)
        resp_dict = json.loads(response.content)
        self.assertIs(resp_dict['state'], True)
        self.assertEquals(resp_dict['data'], u'不命中')
