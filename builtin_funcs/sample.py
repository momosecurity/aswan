# coding=utf-8

from builtin_funcs import BuiltInFuncs


@BuiltInFuncs.register(desc=u'异常用户',
                       args_type_tuple=(('user_id', str),),
                       supported_ops=('is', 'is_not'))
def is_abnormal(req_body):
    user_id = req_body['user_id']
    user_key = user_id[-1]

    # 特殊用户，直接放过
    if user_key == '0':
        return None

    if user_key in {'1', '2', '3', '4'}:
        # 若符合判定条件，则认为命中
        return True
    else:
        # 否则不命中
        return False


@BuiltInFuncs.register(desc=u'历史登录次数',
                       args_type_tuple=(('user_id', str),),
                       supported_ops=('gt', 'ge', 'lt', 'le', 'eq', 'neq'),
                       threshold_trans_func=int
                       )
def user_login_count(req_body):
    user_id = req_body['user_id']
    user_key = user_id[-1]

    # 未获取到值 / 特殊用户直接放过
    if user_key == '0':
        return None

    # 通过各种方法(http,硬编码,rpc等等方式)得到用户在此维度上的值
    if user_id[-1] in {'1', '2', '3', '4'}:
        return 40
    else:
        return 200
