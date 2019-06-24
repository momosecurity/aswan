# coding=utf-8

class QueryException(Exception):
    """ 查询接口出现错误 """
    pass


class BuiltInFuncNotExistError(QueryException):
    """ 内置函数不存在 """
    pass


class RuleNotExistsException(QueryException):
    """ 规则不存在/有错误 """
    pass


class ReportException(Exception):
    """ 上报接口出现错误 """
    pass
