# coding=utf8

import re
import json
import time
from datetime import datetime

from django.http import Http404
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, View
from braces.views import JSONResponseMixin
from redis import RedisError

from core.generic import ListView
from core.utils import errors_to_dict
from core.redis_client import get_redis_client

from builtin_funcs import BuiltInFuncs
from rule.forms import RulesForm, RulesTestForm, CONTROL_MAP, \
    RulesFilterForm, CONTROL_CHOICES
from rule.tables import RulesTable
from risk_models.strategy import Strategys

__all__ = ['RulesListView', 'RulesCreateView', 'RulesDestroyView',
           'RulesChangeView', 'RulesDetailView', 'RulesTestView',
           'RulesDataView', 'RulesEdit']


class RulesCreateView(JSONResponseMixin, TemplateView):
    template_name = "rule/rules_create.html"
    form_class = RulesForm

    def get_context_data(self, **kwargs):
        context = super(RulesCreateView, self).get_context_data(**kwargs)
        form = self.form_class()
        context["form"] = form
        context['strategys'] = form.strategy_names
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST, request=request)
        if form.is_valid():
            rule_id, rule_uuid = form.save()
            data = dict(
                rule_id=rule_id,
                uuid=rule_uuid,
                state=True,
                redirect_url=reverse("rule:list")
            )
        else:
            data = dict(
                state=False,
                error=errors_to_dict(form.errors)
            )
        return self.render_json_response(data)


class RulesDestroyView(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        uuid_ = request.POST.get('id', None)
        if uuid_:
            client = get_redis_client()
            name = 'rule:{}'.format(uuid_)
            client.delete(name)
            return self.render_json_response({
                'state': True,
                'msg': "ok"
            })
        return self.render_json_response({
            'state': False,
            'error': u"未找到规则"
        })


class RulesListView(ListView):
    template_name = "rule/rules_list.html"
    enable_page_size_config = True
    table_class = RulesTable
    filter_form = RulesFilterForm

    def get_queryset(self):
        form_obj = self.filter_form(data=self.request.GET)
        form_obj.full_clean()

        status, rule_name = form_obj.cleaned_data.get(
            'status'), form_obj.cleaned_data.get('rule_name')

        client = get_redis_client()
        result = []
        for rule_key in client.scan_iter(match="rule:*"):
            rule_config = client.hgetall(rule_key)
            if status and rule_config.get('status', '') != status:
                continue
            if rule_name and rule_name not in rule_config.get('title', ''):
                continue
            result.append(rule_config)
        return result

    def get_filter_form(self):
        return self.filter_form(data=self.request.GET)


class RulesChangeView(JSONResponseMixin, View):
    def _parse_data(self, request):
        now = str(int(time.time()))
        origin = request.POST
        uuid_ = origin.get('id')
        status = origin.get('status')

        if status not in ('on', 'off'):
            raise ValueError(u"状态不合法")

        ret = {
            "uuid": uuid_,
            "status": status,
            'user': request.user.username,
            'update_time': now
        }

        end_time = origin.get('end_time')
        #  仅修改状态
        if not end_time:
            return ret

        try:
            datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            raise ValueError(u"结束时间格式不合法")

        ret['end_time'] = end_time

        try:
            title = origin['title']
        except KeyError:
            raise ValueError(u"规则名称必须填写")
        try:
            describe = origin['describe']
        except KeyError:
            raise ValueError(u"规则描述必须填写")

        names = origin.get('names', '').split(':::')
        weights = origin.get('weights', '').split(',')
        strategys = origin.get('strategys', '').split('|')
        controls = origin.get('controls', '').split(',')
        customs = origin.get('customs', '').split(':::')
        lst = [names, weights, strategys, controls, customs]

        for elem in lst[1:]:
            if len(elem) != len(lst[0]):
                raise ValueError(u"数据长度不匹配")
        for weight in weights:
            if not weight.isdigit():
                raise ValueError(u"权重不是整数")
        strategys_list = []
        for strategy_str in strategys:
            try:
                strategy = json.loads(strategy_str)
            except ValueError:
                strategy = strategy_str
            if isinstance(strategy, list):
                strategys_list.append(strategy)
            else:
                strategy_obj = Strategys()
                lst = []
                for uuid_ in strategy.split(';'):
                    lst.append([uuid_,
                                strategy_obj.get_thresholds(uuid_),
                                strategy_obj.get_strategy_name(uuid_)])
                strategys_list.append(lst)
        strategys = strategys_list
        strategy_uuids = []
        for strategy in strategys:
            item = [x[0] for x in strategy]
            item.sort()
            strategy_uuids.append("".join(item))
        if len(set(strategy_uuids)) < len(strategy_uuids):
            raise ValueError(u"策略原子有重复")
        for key in (
                'title', 'describe', 'names', 'weights', 'strategys',
                'controls',
                'customs'):
            ret[key] = locals()[key]
        return ret

    def _build_key_value(self, data):
        #  此时只改阈值
        items = [['user', data['user']], ['update_time', data['update_time']]]
        if not data.get('end_time'):
            key = 'status'
            #  兼容前端，前端传过来的状态为当前状态，而非目标状态
            value = 'on' if data['status'] == 'off' else 'off'
            items.append([key, value])
            return items

        for key in ('title', 'describe', 'status', 'end_time'):
            items.append([key, data[key]])
        strategy_list = []
        datas = zip(data['names'], data['strategys'], data['controls'],
                    data['customs'], data['weights'])
        for (name, strategy, control, custom, weight) in datas:
            d = {}
            d['name'] = name
            d['custom'] = custom
            d['control'] = control
            d['weight'] = weight
            d['strategy_list'] = strategy
            strategy_list.append(d)
        strategy_list = sorted(strategy_list, key=lambda x: int(x["weight"]),
                               reverse=True)
        items.append(['strategys', json.dumps(strategy_list)])
        return items

    def post(self, request, *args, **kwargs):
        try:
            data = self._parse_data(request)
        except ValueError as e:
            return self.render_json_response({
                'state': False,
                'error': str(e),
            })
        client = get_redis_client()
        name = 'rule:{}'.format(data['uuid'])

        for key, value in self._build_key_value(data):
            client.hset(name, key, value)
        return self.render_json_response({
            'state': True,
            'redirect_url': reverse("rule:detail")
        })


class RulesDetailView(JSONResponseMixin, TemplateView):
    template_name = 'rule/rules_detail.html'

    def get_context_data(self, **kwargs):
        context = super(RulesDetailView, self).get_context_data(**kwargs)
        context["rule"] = self.get_rule()
        return context

    def get_rule(self):
        uuid_ = self.request.GET.get('id')
        data = {}
        client = get_redis_client()
        name = 'rule:{}'.format(uuid_)
        d = client.hgetall(name)
        if not d:
            raise Http404
        for key in ('status', 'title', 'describe', 'end_time', 'id', 'uuid'):
            data[key] = d[key]
        try:
            rule_list = json.loads(d["strategys"])
        except ValueError:
            rule_list = []
        for rule in rule_list:
            rule['group_name'] = rule['name']
            rule['weight'] = rule.get('weight', '')
            rule['control_display'] = CONTROL_MAP.get(rule['control'],
                                                      rule['control'])
            rule['strategy_name'] = ";".join(
                x[2] for x in rule['strategy_list'] if len(x) == 3)
            rule['strategy_list_str'] = json.dumps(rule['strategy_list'])
        data['rule_list'] = rule_list
        return data


class RulesTestView(JSONResponseMixin, TemplateView):
    template_name = "rule/rules_test.html"
    form_class = RulesTestForm

    def get_context_data(self, **kwargs):
        context = super(RulesTestView, self).get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            uuid_ = request.POST.get('rule')
            name = "rule:{}".format(uuid_)
            conn = get_redis_client()
            id_ = conn.hget(name, 'id')
            req_body = form.cleaned_data['req_body']
            if not isinstance(req_body, list):
                req_body = [req_body]
            from risk_models.rule import calculate_rule
            results = []
            for req in req_body:
                result, _ = calculate_rule(id_, req)
                results.append(CONTROL_MAP[result])
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


class RulesDataView(JSONResponseMixin, View):
    def _get_one_kind_fields_from_uuids(self, uuids, kind, field, client):
        fields = []
        for uuid_ in uuids:
            name = '%s:%s' % (kind, uuid_)
            value = client.hget(name, field)
            if value:
                fields.append(value)
        return fields

    def _get_bool_strategy_args(self, uuids, client):
        ret = set()
        strategy_funcs = self._get_one_kind_fields_from_uuids(
            uuids, 'bool_strategy', 'strategy_func', client
        )
        for name in strategy_funcs:
            for arg in BuiltInFuncs.get_required_args(name):
                ret.add(arg)
        return ret

    def _get_freq_strategy_args(self, uuids, client):
        ret = set()
        strategy_bodys = self._get_one_kind_fields_from_uuids(
            uuids, 'freq_strategy', 'strategy_body', client
        )
        for names in strategy_bodys:
            for name in names.split(','):
                ret.add(name)
        return ret

    def _get_menu_strategy_args(self, uuids, client):
        ret = set()
        dimensions = self._get_one_kind_fields_from_uuids(
            uuids, 'strategy_menu', 'dimension', client
        )
        for name in dimensions:
            ret.add(name)
        return ret

    def _get_user_strategy_args(self, uuids, client):
        ret = {"user_id"}  # 限制用户型策略，须有userid
        strategy_bodys = self._get_one_kind_fields_from_uuids(
            uuids, 'user_strategy', 'strategy_body', client
        )
        for name in strategy_bodys:
            for name in name.split(','):
                ret.add(name)
        return ret

    def post(self, request, *args, **kwargs):
        uuid_ = request.POST.get('uuid', None)
        if uuid_:
            client = get_redis_client()
            name = 'rule:{}'.format(uuid_)
            try:
                strategy_group_list = json.loads(
                    client.hget(name, 'strategys'))
                strategy_list = [d['strategy_list'][0] for d in
                                 strategy_group_list]
                uuids = [x[0] for x in strategy_list]
                members = (self._get_bool_strategy_args(uuids, client) |
                           self._get_freq_strategy_args(uuids, client) |
                           self._get_menu_strategy_args(uuids, client) |
                           self._get_user_strategy_args(uuids, client))
            except Exception:
                return self.render_json_response({
                    'state': False
                })
            req_body = {}
            for member in members:
                req_body[member] = "xxxxxx"
            return self.render_json_response({
                'state': True,
                'req_body': req_body
            })
        else:
            return self.render_json_response({
                'state': False
            })


class RulesThresholdEdit(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):

        try:
            data = json.loads(request.POST.get('data', '{}'))
            # 从参数中获取需要修改的规则uuid
            rule_uuid = data.get('rule_uuid', None)
            # 从参数中获取需要修改的策略组的下标
            strategy_index = data.get('strategy_index', None)
            # 从参数中获取前端传参过来的策略列表
            new_strategy_confs = data.get('strategy_list', None)
            assert strategy_index is not None
            assert isinstance(strategy_index, int) and strategy_index >= 0
            assert all((rule_uuid, new_strategy_confs))
        except (AssertionError, TypeError, ValueError):
            return self.render_json_response({'state': False, 'msg': '参数校验失败'})

        client = get_redis_client()

        try:
            # 从redis中获取需要修改的规则所有数据
            rule_conf = client.hgetall("rule:{}".format(rule_uuid))
            # 从规则数据中获取策略组数据列表
            strategy_confs = json.loads(rule_conf.get('strategys'))
            # 从策略组列表中找出需要编辑的策略组
            strategy_conf = strategy_confs[strategy_index]
        except (TypeError, ValueError, IndexError, RedisError):
            return self.render_json_response({'state': False, 'msg': '配置读取失败'})

        strategys_obj = Strategys()
        strategy_conf['strategy_list'] = [
            [
                x['strategy_uuid'],
                x['threshold_list'],
                strategys_obj.build_strategy_name_from_thresholds(
                    x['strategy_uuid'], x['threshold_list'])
            ] for x in new_strategy_confs
        ]  # 构造编辑后的策略组

        strategy_confs[strategy_index] = strategy_conf  # 回写策略组
        rule_conf["strategys"] = json.dumps(strategy_confs)
        rule_conf['user'] = request.user.username
        rule_conf['update_time'] = str(int(time.time()))
        try:
            client.hmset("rule:{}".format(rule_uuid), rule_conf)  # 回写规则数据
        except RedisError:
            return self.render_json_response({'state': False, 'msg': '配置回写失败'})

        return self.render_json_response({'state': True})


class RulesEdit(JSONResponseMixin, TemplateView):
    template_name = 'rule/rules_edit.html'

    def get_context_data(self, **kwargs):
        context = super(RulesEdit, self).get_context_data(**kwargs)
        context["rule"] = self.get_rule()
        context['strategys'] = self._get_all_strategys()
        context['controls'] = CONTROL_CHOICES
        return context

    def get_rule(self):
        uuid_ = self.request.GET.get('id')
        if not uuid_:
            raise Http404

        client = get_redis_client()
        name = 'rule:{}'.format(uuid_)
        d = client.hgetall(name)
        if not d:
            raise Http404

        data = {}
        for key in ('status', 'title', 'describe', 'end_time', 'id', 'uuid'):
            data[key] = d[key]

        try:
            rule_list = json.loads(d["strategys"])
        except ValueError:
            rule_list = []
        for rule in rule_list:
            rule['group_name'] = rule['name']
            rule['weight'] = rule.get('weight', '')
            rule['control_display'] = CONTROL_MAP.get(rule['control'],
                                                      rule['control'])
            rule['strategy_name'] = ";".join(
                x[2] for x in rule['strategy_list'] if len(x) == 3)
            rule['strategy_list_str'] = json.dumps(rule['strategy_list'])
        data['rule_list'] = rule_list
        return data

    @classmethod
    def _get_all_strategys(cls):
        return Strategys().get_all_strategy_uuid_and_name()
