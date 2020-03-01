# coding=utf8

import time
import json

from django.urls import reverse
from django.conf import settings
from django.views.generic import TemplateView, View
from braces.views import JSONResponseMixin

from core.generic import ListView
from core.utils import errors_to_dict
from strategy.tables import (
    BoolStrategyTable, FreqStrategyTable, MenuStrategyTable, UserStrategyTable,
)
from strategy.forms import (
    BoolStrategyForm, BoolStrategyTestForm, FreqStrategyForm,
    FreqStrategyTestForm, MenuStrategyForm, MenuStrategyTestForm,
    UserStrategyForm, UserStrategyTestForm,
    FREQ_STRATEGY_UNIQ_SET_KEYS, USER_STRATEGY_UNIQ_SET_KEYS,
    StrategyFilterForm
)
from core.redis_client import get_redis_client
from builtin_funcs import BuiltInFuncs
from risk_models.strategy import (BoolStrategy, MenuStrategy, UserStrategy,
                                  FreqStrategy)


class BaseStrategyDestoryView(JSONResponseMixin, View):
    key_tpl = ''

    def get_values_sign(self, data):
        raise NotImplementedError('need complete')

    def post(self, request, *args, **kwargs):
        uuid = request.POST.get('id', None)
        is_using, rule_id = _check_strategy(uuid)
        if is_using:
            return self.render_json_response(dict(
                state=False,
                error=u"该策略原子正被规则{}引用".format(rule_id)
            ))
        client = get_redis_client()
        name = self.key_tpl.format(uuid=uuid)
        data = client.hgetall(name)
        values_sign = self.get_values_sign(data)
        client.srem(settings.STRATEGY_SIGN_KEY, values_sign)
        client.delete(name)

        return self.render_json_response(dict(
            state=True,
            msg="ok"
        ))


class BoolStrategyDestroyView(BaseStrategyDestoryView):
    key_tpl = 'bool_strategy:{uuid}'

    def get_values_sign(self, data):
        data.pop('uuid')
        data.pop('strategy_desc')
        data.pop('strategy_name')
        keys = sorted(data.keys())
        values_sign = "".join([data[x] for x in keys])
        return values_sign


class BaseStrategyCreateView(JSONResponseMixin, TemplateView):
    template_name = None
    form_class = None
    redirect_view_name = ''

    def get_context_data(self, **kwargs):
        context = super(BaseStrategyCreateView, self).get_context_data(
            **kwargs)
        context['form'] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST, request=request)
        if form.is_valid():
            uuid_ = form.save()
            data = dict(
                uuid=uuid_,
                state=True,
                redirect_url=reverse(self.redirect_view_name)
            )
        else:
            data = dict(
                state=False,
                error=errors_to_dict(form.errors)
            )
        return self.render_json_response(data)


class BaseStrategyListView(ListView):
    template_name = None
    enable_page_size_config = True
    table_class = None
    key_prefix = None

    def get_filter_form(self):
        return StrategyFilterForm(data=self.request.GET)

    def get_all_strategy_configs(self):
        client = get_redis_client()
        return [client.hgetall(name) for name in
                client.scan_iter(match=self.key_prefix)]

    def get_queryset(self):
        filter_name = self.request.GET.get('filter_name', '')
        return [config for config in self.get_all_strategy_configs() if
                filter_name in config['strategy_name']]


class BoolStrategyListView(BaseStrategyListView):
    template_name = "strategy/bool_strategy_list.html"
    table_class = BoolStrategyTable
    key_prefix = 'bool_strategy:*'


class BoolStrategyCreateView(BaseStrategyCreateView):
    template_name = "strategy/bool_strategy_create.html"
    form_class = BoolStrategyForm
    redirect_view_name = 'strategy:bool_strategy_list'


class BoolStrategyTestView(JSONResponseMixin, TemplateView):
    template_name = "strategy/bool_strategy_test.html"
    form_class = BoolStrategyTestForm

    def get_context_data(self, **kwargs):
        context = super(BoolStrategyTestView, self).get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            uuid_ = request.POST.get('strategy')
            req_body = request.POST.get('req_body', '')
            req_body = json.loads(req_body)
            client = get_redis_client()
            name = 'bool_strategy:{}'.format(uuid_)
            d = client.hgetall(name)
            strategy = BoolStrategy(d)

            func = strategy.get_callable()
            if not isinstance(req_body, list):
                req_body = [req_body]
            results = []
            for req in req_body:
                resp = func(req)
                if resp:
                    results.append(u"命中")
                else:
                    results.append(u"不命中")
            if len(results) == 1:
                results = results[0]
            data = dict(
                state=True,
                data=results
            )
        else:
            data = dict(
                state=False,
                error=errors_to_dict(form.errors)
            )
        return self.render_json_response(data)


class BoolStrategyDataView(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        uuid = request.POST.get('uuid', None)
        if uuid:
            client = get_redis_client()
            name = 'bool_strategy:{}'.format(uuid)
            d = client.hgetall(name)
            strategy_func = d['strategy_func']
            required_args = BuiltInFuncs.get_required_args(strategy_func)
            req_body = {}
            for member in required_args:
                req_body[member] = "xxxxxx"
            return self.render_json_response({
                'state': True,
                'req_body': req_body
            })
        else:
            return self.render_json_response({
                'state': False
            })


class FreqStrategyListView(BaseStrategyListView):
    template_name = "strategy/freq_strategy_list.html"
    table_class = FreqStrategyTable
    key_prefix = 'freq_strategy:*'


class FreqStrategyCreateView(BaseStrategyCreateView):
    template_name = "strategy/freq_strategy_create.html"
    form_class = FreqStrategyForm
    redirect_view_name = 'strategy:freq_strategy_list'


class FreqStrategyDestroyView(BaseStrategyDestoryView):
    key_tpl = 'freq_strategy:{uuid}'

    def get_values_sign(self, data):
        values_sign = ":".join(
            [str(data[x]) for x in FREQ_STRATEGY_UNIQ_SET_KEYS])
        return values_sign


class FreqStrategyTestView(JSONResponseMixin, TemplateView):
    template_name = "strategy/freq_strategy_test.html"
    form_class = FreqStrategyTestForm

    def get_context_data(self, **kwargs):
        context = super(FreqStrategyTestView, self).get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            uuid_ = request.POST.get('strategy', '')
            req_body = form.cleaned_data["req_body"]
            history_data = form.cleaned_data['history_data'] or None

            client = get_redis_client()
            name = 'freq_strategy:{}'.format(uuid_)
            d = client.hgetall(name)
            strategy_time = int(d['strategy_time'])
            threshold = int(d['strategy_limit'])
            strategy = FreqStrategy(d)

            if not isinstance(req_body, list):
                req_body = [req_body]
            if history_data:
                func = strategy.get_callable()
                raw_results = [func(req, history_data) for req in req_body]
            else:
                func = strategy.get_callable_from_threshold_list(
                    [strategy_time, threshold])
                raw_results = [func(req) for req in req_body]
            results = [u"命中" if i else u"不命中" for i in raw_results]
            if len(results) == 1:
                results = results[0]
            data = dict(
                state=True,
                data=results,
            )
        else:
            data = dict(
                state=False,
                error=errors_to_dict(form.errors)
            )
        return self.render_json_response(data)


class FreqStrategyDataView(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        uuid = request.POST.get('uuid', None)
        if uuid:
            client = get_redis_client()
            name = 'freq_strategy:{}'.format(uuid)
            d = client.hgetall(name)
            strategy_body = d['strategy_body']
            members = strategy_body.split(",")
            history = {}
            req_body = {}
            for member in members:
                history[member] = "xxxxxx"
                req_body[member] = "xxxxxx"
            ts = int(time.time())
            history_data = []
            for _ in range(3):
                history["timestamp"] = ts
                history_data.append(history)
            return self.render_json_response({
                'state': True,
                'history_data': history_data,
                'req_body': req_body
            })
        else:
            return self.render_json_response({
                'state': False
            })


class MenuStrategyDestroyView(BaseStrategyDestoryView):
    key_tpl = 'strategy_menu:{uuid}'

    def get_values_sign(self, data):
        data.pop("strategy_desc", None)
        data.pop("strategy_name", None)
        data.pop("uuid", None)
        keys = sorted(data.keys())
        values_sign = "".join([data[x] for x in keys])
        return values_sign


class MenuStrategyListView(BaseStrategyListView):
    template_name = "strategy/menu_strategy_list.html"
    table_class = MenuStrategyTable
    key_prefix = 'strategy_menu:*'


class MenuStrategyCreateView(BaseStrategyCreateView):
    template_name = "strategy/menu_strategy_create.html"
    form_class = MenuStrategyForm
    redirect_view_name = 'strategy:menu_strategy_list'


class MenuStrategyTestView(JSONResponseMixin, TemplateView):
    template_name = "strategy/menu_strategy_test.html"
    form_class = MenuStrategyTestForm

    def get_context_data(self, **kwargs):
        context = super(MenuStrategyTestView, self).get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = MenuStrategyTestForm(data=request.POST)
        if form.is_valid():
            uuid_ = request.POST.get('strategy')
            req_body = form.cleaned_data['req_body']

            results = []
            client = get_redis_client()
            name = 'strategy_menu:{}'.format(uuid_)
            d = client.hgetall(name)
            strategy = MenuStrategy(d)
            func = strategy.get_callable()

            if not isinstance(req_body, list):
                req_body = [req_body]
            for req in req_body:
                res = func(req)
                results.append(u"命中" if res else u"不命中")
            if len(results) == 1:
                results = results[0]

            data = dict(
                state=True,
                data=results
            )
        else:
            data = dict(
                state=False,
                error=errors_to_dict(form.errors)
            )
        return self.render_json_response(data)


class MenuStrategyDataView(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        uuid = request.POST.get('uuid', None)
        if uuid:
            client = get_redis_client()
            name = 'strategy_menu:{}'.format(uuid)
            d = client.hgetall(name)
            dimension = d['dimension']
            req_body = {dimension: "xxxxx"}
        else:
            req_body = {}
        return self.render_json_response({
            'state': True,
            'req_body': req_body
        })


class UserStrategyListView(BaseStrategyListView):
    template_name = "strategy/user_strategy_list.html"
    table_class = UserStrategyTable
    key_prefix = 'user_strategy:*'


class UserStrategyCreateView(BaseStrategyCreateView):
    template_name = "strategy/user_strategy_create.html"
    form_class = UserStrategyForm
    redirect_view_name = 'strategy:user_strategy_list'


class UserStrategyDestroyView(BaseStrategyDestoryView):
    key_tpl = 'user_strategy:{uuid}'

    def get_values_sign(self, data):
        values_sign = ":".join(
            [str(data[x]) for x in USER_STRATEGY_UNIQ_SET_KEYS])
        return values_sign


class UserStrategyDataView(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        uuid = request.POST.get('uuid', None)
        if uuid:
            client = get_redis_client()
            name = 'user_strategy:{}'.format(uuid)
            d = client.hgetall(name)
            strategy_body = d['strategy_body']
            members = strategy_body.split(",")
            history = {"user_id": "xxxxxx"}
            req_body = {"user_id": "xxxxxx"}
            for member in members:
                history[member] = "yyyyyy"
                req_body[member] = "yyyyyy"
            ts = int(time.time())
            history_data = []
            for _ in range(3):
                history["timestamp"] = ts
                history_data.append(history)
            return self.render_json_response({
                'state': True,
                'history_data': history_data,
                'req_body': req_body
            })
        else:
            return self.render_json_response({
                'state': False
            })


class UserStrategyTestView(JSONResponseMixin, TemplateView):
    template_name = "strategy/user_strategy_test.html"
    form_class = UserStrategyTestForm

    def get_context_data(self, **kwargs):
        context = super(UserStrategyTestView, self).get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            uuid_ = form.cleaned_data['strategy']
            req_body = form.cleaned_data["req_body"]
            history_data = form.cleaned_data['history_data'] or None

            client = get_redis_client()
            name = 'user_strategy:{}'.format(uuid_)
            d = client.hgetall(name)
            strategy = UserStrategy(d)
            strategy_day = int(d['strategy_day'])
            threshold = int(d['strategy_limit'])

            if not isinstance(req_body, list):
                req_body = [req_body]
            if history_data:
                func = strategy.get_callable()
                raw_results = [func(req, history_data) for req in req_body]
            else:
                func = strategy.get_callable_from_threshold_list(
                    [strategy_day, threshold])
                raw_results = [func(req) for req in req_body]
            results = [u"命中" if i else u"不命中" for i in raw_results]
            if len(results) == 1:
                results = results[0]
            data = dict(
                state=True,
                data=results,
            )
        else:
            data = dict(
                state=False,
                error=errors_to_dict(form.errors)
            )
        return self.render_json_response(data)


def _check_strategy(strategy_id):
    """校验策略原子是否被生效中的规则引用"""
    client = get_redis_client()
    for r in client.scan_iter(match="rule:*"):
        rule = client.hgetall(r)
        strategy_group_list = json.loads(rule.get("strategys", '[]'))
        for strategy_group in strategy_group_list:
            strategy_list = strategy_group.get("strategy_list", [])
            for stategy_data in strategy_list:
                if stategy_data and stategy_data[0] == strategy_id:
                    return True, rule["id"]
    return False, None
