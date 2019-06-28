# coding=utf-8

from core.testcase import BaseTestCase

from django.core.urlresolvers import reverse


class TestPermission(BaseTestCase):
    users_url = 'permissions:users'
    users_update_url = 'permissions:user_update'

    groups_url = 'permissions:groups'
    group_update_url = 'permissions:group_update'
    group_create_url = 'permissions:group_create'

    uri_group_url = 'permissions:uri_groups'
    uri_group_update_url = 'permissions:uri_group_update'
    uri_group_create_url = 'permissions:uri_group_create'

    def _test_users(self):
        users_url = reverse(self.users_url)

        # 直接访问
        response = self.client.get(users_url)
        self.assertEquals(response.status_code, 200)

        # 带参访问
        data = {
            'fullname': 'fullname',
            'pk': 'email'
        }
        response = self.client.get(users_url, data=data)
        self.assertEquals(response.status_code, 200)

    def test_view(self):
        self._test_users()
