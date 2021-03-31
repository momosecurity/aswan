# coding=utf-8
import json
from collections import defaultdict

from django.dispatch import Signal, receiver

from www.log_manage.models import AuditLogModel

__all__ = ['user_visit']

# 用户访问
user_visit = Signal(providing_args=['request', 'response'])


def get_username(user):
    if not user:
        return ""
    return user.last_name + user.first_name


default_ignore_args = {"submit"}
ignore_post_args = {"csrfmiddlewaretoken"}


@receiver(user_visit, sender=None)
def record_access_log(request, response, **kwargs):
    # 忽略访客请求
    if not request.user.pk:
        return

    email = request.user.email if request.user else ""
    username = get_username(request.user)

    path = request.path
    method = request.method

    if method == 'POST':
        ignore_args = ignore_post_args
    else:
        ignore_args = default_ignore_args

    # 此处收集全部参数
    req_body = {}
    for req in (request.GET, request.POST):
        req_body.update({k: req[k] for k in req if
                         k not in ignore_args})

    AuditLogModel.objects.create(
        username=username,
        email=email,
        path=path,
        method=method,
        status=response.status_code,
        req_body=json.dumps(req_body, ensure_ascii=False),
    )
