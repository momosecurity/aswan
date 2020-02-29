# coding=utf8

import os

from django.test import TransactionTestCase

from core.redis_client import get_redis_client
from core.pymongo_client import get_mongo_client

from permissions.init_data import create_user

__all__ = ['BaseTestCase']


def _get_test_mongo_client(db_name='test_risk_control'):
    return get_mongo_client(db_name)


class BaseTestCase(TransactionTestCase):
    username = 'test_superuser'
    password = 'test_test'
    email = 'test@immomo.com'

    def setUp(self):
        """为单元测试方法提供登录功能"""
        super(BaseTestCase, self).setUp()
        self.client.login(username=self.username, password=self.password)

    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        risk_env = os.environ.get('RISK_ENV')
        assert risk_env and risk_env == 'test', '注意，此部分只能在测试环境中执行'
        create_user(email=cls.email, username=cls.username,
                    password=cls.password, is_superuser=1)

    @classmethod
    def tearDownClass(cls):
        super(BaseTestCase, cls).tearDownClass()

        # 清理测试库
        db = get_mongo_client()
        db.client.drop_database(db.name)

        client = get_redis_client()
        client.flushdb()
