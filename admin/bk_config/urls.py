# coding=utf8

from django.conf.urls import url
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from bk_config.views import (
    ConfigSourceListView, ConfigSourceAjaxView, ConfigSourceCreateView,
    ConfigDestroyView
)

urlpatterns = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy("config:source_list"),
                                    permanent=True), name="config_index"),

    url(r'^source/list/$', ConfigSourceListView.as_view(), name="source_list"),
    url(r'^source/ajax/$', ConfigSourceAjaxView.as_view(), name="source_ajax"),
    url(r'^source/create/$', ConfigSourceCreateView.as_view(),
        name="source_create"),
    url(r'^source/destroy/$', ConfigDestroyView.as_view(),
        name="source_destroy"),
]
