# coding=utf-8

import unittest

from builtin_funcs.base import BuiltInFuncs
from builtin_funcs.sample import is_abnormal, user_login_count
from risk_models.exceptions import BuiltInFuncNotExistError


class TestSampleFunction(unittest.TestCase):

    def test_is_abnormal(self):
        testcases = [
            ({'user_id': '111110'}, None),
            ({'user_id': '111111'}, True),
            ({'user_id': '111118'}, False),
        ]
        for req_body, result in testcases:
            self.assertEquals(is_abnormal(req_body), result)

    def test_user_login_count(self):
        testcases = [
            ({'user_id': '111110'}, None),
            ({'user_id': '111111'}, 40),
            ({'user_id': '111118'}, 200),
        ]
        for req_body, result in testcases:
            self.assertEquals(user_login_count(req_body), result)


class TestBaseFunction(unittest.TestCase):

    def test_is_and_is_not(self):
        func_code = 'is_abnormal'
        testcases = [
            ({'user_id': '111110'}, None),
            ({'user_id': '111111'}, True),
            ({'user_id': '111118'}, False),
        ]
        for req_body, result in testcases:
            self.assertEquals(BuiltInFuncs.run(req_body, func_code, 'is'),
                              False if result is None else result)
            self.assertEquals(BuiltInFuncs.run(req_body, func_code, 'is_not'),
                              False if result is None else not result)

    def test_op(self):
        func_code = 'user_login_count'
        no_exists_func_code = 'test:func_no_exists'
        op_result_map = {
            'lt': False,
            'le': True,
            'gt': False,
            'ge': True,
            'eq': True,
            'ne': False,
        }
        testcases = [
            ({'user_id': '111110'}, None),
            ({'user_id': '111111'}, 40),
            ({'user_id': '111118'}, 200),
        ]

        for req_body, value in testcases:
            threshold = value or 1000
            for op_code, result in op_result_map.items():
                self.assertEquals(
                    BuiltInFuncs.run(req_body, func_code, op_code,
                                     threshold=threshold),
                    False if value is None else result)

                with self.assertRaises(BuiltInFuncNotExistError):
                    BuiltInFuncs.run(req_body, no_exists_func_code, op_code,
                                     threshold=threshold)

    def test_args_not_enough(self):
        func_code = 'is_abnormal'
        req_body = {'no_exists_key': 1}

        self.assertEquals(BuiltInFuncs.run(req_body, func_code, 'is'), False)

    def test_args_method(self):
        func_code = 'is_abnormal'
        self.assertEquals(BuiltInFuncs.get_required_args(func_code),
                          ['user_id'])

    def test_repr(self):
        func_code = 'is_abnormal'
        buildin_func_obj = BuiltInFuncs.name_callable.get(func_code)
        self.assertEquals(repr(buildin_func_obj), buildin_func_obj.desc)


if __name__ == '__main__':
    unittest.main()
