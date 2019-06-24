# coding=utf-8
import json
from datetime import datetime, timedelta

from django.core.urlresolvers import reverse

from core.utils import get_sample_str
from menu.forms import MENU_TYPE_CHOICES_ADD_CHOICES
from menu.init_data import create_menu_event, add_element_to_menu

from core.testcase import BaseTestCase


class TestMenuMinix(object):
    create_uri = 'menus:create'
    delete_uri = 'menus:delete'
    list_uri = ''
    test_cases = []

    def _test_list(self):
        # todo 这里的参数有些问题，降低了覆盖率，后续改一下
        data = {'dimension': self.dimension, 'menu_type': 'black',
                'event': self.event_code}
        response = self.client.get(reverse(self.list_uri), data=data)
        self.assertEquals(response.status_code, 200)

    def _test_destroy(self):

        # 参数不全
        resp = self.client.post(reverse(self.delete_uri))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(json.loads(resp.content)['error'], u"id不合法")

        # ID格式错误
        menu_element_id = get_sample_str(24)
        resp = self.client.post(reverse(self.delete_uri),
                                data={'ids': menu_element_id})
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(json.loads(resp.content)['error'], u"id不合法")

        # 成功删除
        menu_element_id = add_element_to_menu(self.event_code, 'black',
                                              self.dimension, 'test_value')
        resp = self.client.post(reverse(self.delete_uri), data={'ids': menu_element_id})
        self.assertEquals(resp.status_code, 200)
        t = json.loads(resp.content)
        self.assertEquals(t['state'], True)

        # 删除不存在的记录
        resp = self.client.post(reverse(self.delete_uri),
                                data={'ids': menu_element_id})
        self.assertEquals(resp.status_code, 200)
        t = json.loads(resp.content)
        self.assertEquals(t['error'], u"记录均不存在")

    def _test_create(self):
        end_time = (datetime.now() + timedelta(days=1))

        for menu_type, _ in MENU_TYPE_CHOICES_ADD_CHOICES:
            for value, state in self.test_cases:
                data = {
                    'value': value,
                    'dimension': self.dimension,
                    'menu_type': menu_type,
                    'event_code': self.event_code,
                    'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'menu_desc': 'test'
                }
                # 首次创建
                resp = self.client.post(reverse(self.create_uri), data=data)
                self.assertEquals(resp.status_code, 200)
                t = json.loads(resp.content)
                self.assertEquals(t['state'], state)

                # 重复创建只会更新
                resp = self.client.post(reverse(self.create_uri), data=data)
                self.assertEquals(resp.status_code, 200)
                t = json.loads(resp.content)
                self.assertEquals(t['state'], state)

                # 错误的结束时间
                t_end_time = end_time - timedelta(days=3)
                data['end_time'] = t_end_time.strftime('%Y-%m-%d %H:%M:%S')
                resp = self.client.post(reverse(self.create_uri), data=data)
                self.assertEquals(resp.status_code, 200)
                t = json.loads(resp.content)
                self.assertEquals(t['state'], False)

    def test_view(self):
        self.event_code = create_menu_event()['event_code']

        self._test_create()
        self._test_list()
        self._test_destroy()


class TestPayMenu(TestMenuMinix, BaseTestCase):
    dimension = 'pay'
    test_cases = [(get_sample_str(10), True)]
    list_uri = 'menus:pay_list'


class TestUidMenu(TestMenuMinix, BaseTestCase):
    dimension = 'uid'
    test_cases = [(get_sample_str(10), True)]
    list_uri = 'menus:uid_list'


class TestUserIDMenu(TestMenuMinix, BaseTestCase):
    dimension = 'user_id'
    test_cases = [(get_sample_str(10), True)]
    list_uri = 'menus:userid_list'


class TestPhoneMenu(TestMenuMinix, BaseTestCase):
    dimension = 'phone'
    test_cases = [(get_sample_str(10), False), ('11111111111', True)]
    list_uri = 'menus:phone_list'


class TestIPMenu(TestMenuMinix, BaseTestCase):
    dimension = 'ip'
    test_cases = [(get_sample_str(7), False), ('1.1.1.1', True)]
    list_uri = 'menus:ip_list'


class TestEventView(BaseTestCase):
    list_uri = 'menus:event_list'
    create_uri = 'menus:event_create'
    destroy_uri = 'menus:event_destroy'

    def _test_create(self):
        data = {'event_name': get_sample_str(10)}
        response = self.client.post(reverse(self.create_uri), data=data)
        self.assertEquals(response.status_code, 200)
        t = json.loads(response.content)
        self.event_code = t['event_code']
        self.assertEquals(t['state'], True)

        response = self.client.post(reverse(self.create_uri), data=data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)['state'], False)

    def _test_destroy(self):
        event_code = self.event_code
        response = self.client.post(reverse(self.destroy_uri),
                                    data={'id': event_code})
        self.assertEquals(response.status_code, 200)

    def _test_list(self):
        response = self.client.get(reverse(self.list_uri))
        self.assertEquals(response.status_code, 200)

    def test_view(self):
        self._test_create()
        self._test_list()
        self._test_destroy()
