# coding=utf8

from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from strategy.views import (
    BoolStrategyListView, BoolStrategyCreateView, BoolStrategyDestroyView,
    BoolStrategyTestView, BoolStrategyDataView,
    FreqStrategyListView, FreqStrategyCreateView, FreqStrategyDestroyView,
    FreqStrategyTestView, FreqStrategyDataView,
    MenuStrategyListView, MenuStrategyCreateView, MenuStrategyDestroyView,
    MenuStrategyTestView, MenuStrategyDataView,
    UserStrategyListView, UserStrategyCreateView, UserStrategyDestroyView,
    UserStrategyTestView, UserStrategyDataView,
)

urlpatterns = [
    url(r'^$',
        RedirectView.as_view(url=reverse_lazy("strategy:menu_strategy_list"),
                             permanent=True), name="strategy_index"),
    # 名单型策略
    url(r'^menu_strategy/list/$', MenuStrategyListView.as_view(),
        name="menu_strategy_list"),
    url(r'^menu_strategy/create/$', MenuStrategyCreateView.as_view(),
        name="menu_strategy_create"),
    url(r'^menu_strategy/destroy/$', MenuStrategyDestroyView.as_view(),
        name="menu_strategy_destroy"),
    url(r'^menu_strategy/test/$', MenuStrategyTestView.as_view(),
        name="menu_strategy_test"),
    url(r'^menu_strategy/data/$', MenuStrategyDataView.as_view(),
        name="menu_strategy_data"),

    # 布尔型策略
    url(r'^bool_strategy/list/$', BoolStrategyListView.as_view(),
        name="bool_strategy_list"),
    url(r'^bool_strategy/create/$', BoolStrategyCreateView.as_view(),
        name="bool_strategy_create"),
    url(r'^bool_strategy/destroy/$', BoolStrategyDestroyView.as_view(),
        name="bool_strategy_destroy"),
    url(r'^bool_strategy/test/$', BoolStrategyTestView.as_view(),
        name="bool_strategy_test"),
    url(r'^bool_strategy/data/$', BoolStrategyDataView.as_view(),
        name="bool_strategy_data"),

    # 时段频控策略
    url(r'^freq_strategy/list/$', FreqStrategyListView.as_view(),
        name="freq_strategy_list"),
    url(r'^freq_strategy/create/$', FreqStrategyCreateView.as_view(),
        name="freq_strategy_create"),
    url(r'^freq_strategy/destroy/$', FreqStrategyDestroyView.as_view(),
        name="freq_strategy_destroy"),
    url(r'^freq_strategy/test/$', FreqStrategyTestView.as_view(),
        name="freq_strategy_test"),
    url(r'^freq_strategy/data/$', FreqStrategyDataView.as_view(),
        name="freq_strategy_data"),

    # 限用户数型策略
    url(r'^user_strategy/list/$', UserStrategyListView.as_view(),
        name="user_strategy_list"),
    url(r'^user_strategy/create/$', UserStrategyCreateView.as_view(),
        name="user_strategy_create"),
    url(r'^user_strategy/destroy/$', UserStrategyDestroyView.as_view(),
        name="user_strategy_destroy"),
    url(r'^user_strategy/test/$', UserStrategyTestView.as_view(),
        name="user_strategy_test"),
    url(r'^user_strategy/data/$', UserStrategyDataView.as_view(),
        name="user_strategy_data"),
]
