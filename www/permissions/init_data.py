# coding=utf-8

import random

from django.contrib.auth.models import User

from permissions.permission import UserPermission


def create_user(email, username, password, is_superuser):
    """
        创建用户, 本意是用于测试，因此只是简单的删掉重建
    :param email:
    :param username: 用户名(登录用)
    :param password: 密码
    :param is_superuser:
    """
    try:
        obj = User.objects.get(username=username)
        obj.delete()
    except User.DoesNotExist:
        pass

    User.objects.create_superuser(username=username,
                                  email=email,
                                  password=password)

    import string
    last_name = ''.join(random.sample(string.ascii_lowercase, 8))
    first_name = ''.join(random.sample(string.ascii_uppercase, 8))
    if not UserPermission.objects.get(email):
        UserPermission(
            email,
            fullname=u'{}{}'.format(last_name, first_name),
            is_superuser=is_superuser
        ).save()
