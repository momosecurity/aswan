# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from permissions.views import (
    UserPermListView, UserPermUpdateView,
    GroupPermListView, GroupPermUpdateView, GroupPermCreateView,
    UriGroupPermListView, UriGroupPermUpdateView, UriGroupPermCreateView,
)


urlpatterns = [
    # user permission
    url(r'^$', login_required(UserPermListView.as_view()), name="index"),
    url(r'^users/$', login_required(UserPermListView.as_view()), name="users"),
    url(r'^user/update/$', login_required(UserPermUpdateView.as_view()), name="user_update"),

    # group permission
    url(r'^groups/$', login_required(GroupPermListView.as_view()), name="groups"),
    url(r'^group/update/$', login_required(GroupPermUpdateView.as_view()), name="group_update"),
    url(r'^group/create/$', login_required(GroupPermCreateView.as_view()), name="group_create"),

    # uri group permission
    url(r'^uri_groups/$', login_required(UriGroupPermListView.as_view()), name="uri_groups"),
    url(r'^uri_group/update/$', login_required(UriGroupPermUpdateView.as_view()), name="uri_group_update"),
    url(r'^uri_group/create/$', login_required(UriGroupPermCreateView.as_view()), name="uri_group_create"),
]
