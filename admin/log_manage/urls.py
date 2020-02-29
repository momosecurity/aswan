# coding=utf8
from django.conf.urls import url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy
from log_manage.views import (HitListDetailView, RuleStrategyMapView,
                              AuditLogListView)

urlpatterns = [
    url(r'^$',
        RedirectView.as_view(url=reverse_lazy("log_manage:hit_list_detail"),
                             permanent=True), name="log_manage_index"),

    url(r'^hit/list_detail/$', HitListDetailView.as_view(),
        name="hit_list_detail"),
    url(r'^rule_strategy_map/$', RuleStrategyMapView.as_view(),
        name="rule_strategy_map"),
    url(r'^audit_log_list/$', AuditLogListView.as_view(), name='audit_logs')
]
