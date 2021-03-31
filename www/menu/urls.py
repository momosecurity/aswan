# coding=utf8
from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from www.menu.views import (UseridListView, MenuCreateView, MenuDestroyView, IpListView,
                        UidListView, PayListView, PhoneListView,
                        EventListView, EventCreateView, EventDestroyView)

urlpatterns = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy("menus:event_list"), permanent=True), name="menu_index"),

    url(r'^common_create/$', MenuCreateView.as_view(), name="create"),
    url(r'^common_delete/$', MenuDestroyView.as_view(), name="delete"),

    url(r'^event/list/$', EventListView.as_view(), name="event_list"),
    url(r'^event/create/$', EventCreateView.as_view(), name="event_create"),
    url(r'^event/destroy/$', EventDestroyView.as_view(), name="event_destroy"),

    url(r'^userid/list/$', UseridListView.as_view(), name="userid_list"),
    url(r'^ip/list/$', IpListView.as_view(), name="ip_list"),
    url(r'^uid/list/$', UidListView.as_view(), name="uid_list"),
    url(r'^pay/list/$', PayListView.as_view(), name="pay_list"),
    url(r'^phone/list/$', PhoneListView.as_view(), name="phone_list"),
]
