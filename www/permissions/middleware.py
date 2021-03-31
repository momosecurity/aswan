# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from www.log_manage.signals import user_visit
from www.permissions.permission import UserPermission, DBError
from risk_models.lru import LRUCacheDict

LOGGER = logging.getLogger(__name__)


class AlwaysInContainer(object):
    def __contains__(self, _):
        return True


always_in_container = AlwaysInContainer()

WHITE_LIST_URIS = {
    '/',
    '/home/',
    '/accounts/login/',
    '/accounts/logout/',
}

CACHE_EXPIRE_TIME = 10 * 60  # 10 minutes
CACHE_HAS_PERMS = LRUCacheDict(max_size=1024, expiration=CACHE_EXPIRE_TIME)
CACHE_USER_PERMS = LRUCacheDict(max_size=100, expiration=CACHE_EXPIRE_TIME)


class PermissionsMiddleware(object):
    @classmethod
    def process_request(cls, request, *args, **kwargs):
        user = request.user
        path = request.path
        if path in WHITE_LIST_URIS:
            return
        if not user.id and not request.is_ajax():
            next_url = reverse("risk_auth:risk_login")
            return redirect(next_url)
        if not cls.has_perm(user.email, path):
            raise PermissionDenied

    @classmethod
    def has_perm(cls, pk, path):
        try:
            return CACHE_HAS_PERMS[(pk, path)]
        except KeyError:
            pass

        result = path in cls.get_user_perms(pk)
        if result:
            CACHE_HAS_PERMS[(pk, path)] = result
        return result

    @classmethod
    def get_user_perms(cls, pk):
        try:
            return CACHE_USER_PERMS[pk]
        except KeyError:
            pass

        user = UserPermission.objects.get(pk)
        if not user:
            return WHITE_LIST_URIS

        if user.is_superuser:
            return always_in_container

        try:
            user_perm = user.perm_uris
            result = user_perm | WHITE_LIST_URIS
            if user_perm:
                CACHE_USER_PERMS[pk] = result
            return result
        except DBError:
            LOGGER.error(u'Failed get user permissions ({}-{}) for DB error!'
                         .format(user.pk, user.fullname))
            return WHITE_LIST_URIS


class UserAuditMiddleware(object):
    ignore_uris = [
        "/accounts/login/",
        "/accounts/logout/",
    ]

    def process_response(self, request, response, *args, **kwargs):
        path = request.path
        method = request.method
        # 忽略部分uri
        if path in self.ignore_uris or '/isolation' in path:
            return response

        # 忽略静态资源请求
        if method == "GET" and "." in path:
            return response
        user_visit.send(sender=self.__class__, request=request,
                        response=response)

        return response
