# coding=utf8
from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from www.rule.views import (RulesListView, RulesCreateView, RulesDestroyView, RulesChangeView,
                        RulesDetailView, RulesTestView, RulesDataView, RulesThresholdEdit,
                        RulesEdit)


urlpatterns = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy("rule:list"), permanent=True), name="rule_index"),
    url(r'^list/$', RulesListView.as_view(), name="list"),
    url(r'^create/$', RulesCreateView.as_view(), name="create"),
    url(r'^destroy/$', RulesDestroyView.as_view(), name="destroy"),
    url(r'^change/$', RulesChangeView.as_view(), name="change"),
    url(r'^detail/$', RulesDetailView.as_view(), name="detail"),
    url(r'^test/$', RulesTestView.as_view(), name="test"),
    url(r'^data/$', RulesDataView.as_view(), name="data"),
    url(r'^edit/$', RulesEdit.as_view(), name="edit"),
    url(r'^threshold_edit/$', RulesThresholdEdit.as_view(), name="threshold_edit"),
]
