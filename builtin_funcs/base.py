# coding=utf8

import logging
from functools import wraps
import operator

from risk_models.exceptions import BuiltInFuncNotExistError

logger = logging.getLogger(__name__)
logging.basicConfig()


class BuiltInFuncs(object):
    name_callable = {}
    name_args_type = {}
    name_supported_ops = {}

    op_map = {
        'lt': operator.lt,
        'le': operator.le,
        'eq': operator.eq,
        'ne': operator.ne,
        'ge': operator.ge,
        'gt': operator.gt,
        'is': operator.is_,
        'is_not': operator.is_not
    }

    def __init__(self, desc, threshold_trans_func, run_func):
        self.desc = desc
        self.threshold_trans_func = threshold_trans_func
        self.run_func = run_func

    @classmethod
    def register(cls, desc, args_type_tuple, supported_ops,
                 threshold_trans_func=None, func_code=None):
        """
            对内置函数进行注册
        :param str|unicode desc: 函数描述(名称)
        :param tuple args_type_tuple: 函数所需参数
        :param tuple|list supported_ops: 内置函数结果所支持的操作符
        :param callable threshold_trans_func: 阈值转化函数
        :return:
        """

        def outer(func):
            obj = cls(desc=desc, threshold_trans_func=threshold_trans_func,
                      run_func=func)

            code = func_code or func.__name__
            cls.name_callable[code] = obj
            cls.name_args_type[code] = args_type_tuple
            cls.name_supported_ops[code] = supported_ops

            @wraps(func)
            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            return inner

        return outer

    @classmethod
    def check_args(cls, name, req_body):
        """
            校验请求参数是否合法(满足内置函数所需)
        :param str|unicode name: 内置函数code
        :param dict req_body: 请求参数
        :return:
        """
        args_type_tuple = cls.name_args_type[name]
        for k, type_ in args_type_tuple:
            value = req_body.get(k)
            if value is None or not isinstance(req_body[k], type_):
                return False
        return True

    @classmethod
    def get_required_args(cls, name):
        """
            得到内置函数所需的key
        :param str|unicode name: 函数code
        :return:
        """
        args_type_tuple = cls.name_args_type[name]
        return [k1 for (k1, k2) in args_type_tuple]

    def trans_result(self, rv, op_name, threshold):
        """
            对结果进行转化，最后结果为 True/False 标识是否命中
        :param bool|None rv: 内置函数返回值
        :param str|unicode op_name: 操作符
        :param object threshold: 阈值
        :return:
        """
        #  若想忽略op码永远通过则设置rv为None
        if rv is None:
            return False

        if op_name in {'is', 'is_not'}:
            threshold = True
        elif self.threshold_trans_func:
            threshold = self.threshold_trans_func(threshold)

        method = self.op_map.get(op_name, None)
        return method(rv, threshold) if method else False

    def __call__(self, req_body, op_name, threshold, **kwargs):
        if not self.check_args(self.run_func.__name__, req_body):
            logger.error('run %s with invalid req_body(%s)', self, req_body)
            return False

        rv = self.run_func(req_body, **kwargs)
        return self.trans_result(rv, op_name, threshold)

    def __repr__(self):
        return self.desc

    @classmethod
    def run(cls, req_body, builtin_func_name, op_name, threshold=None,
            **kwargs):
        obj = cls.name_callable.get(builtin_func_name)
        if obj is None:
            raise BuiltInFuncNotExistError(
                '{} does not exist'.format(builtin_func_name)
            )
        return obj(req_body, op_name, threshold, **kwargs)
