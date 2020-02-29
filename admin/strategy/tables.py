# coding=utf8
import json

from django.utils.translation import ugettext_lazy as _
from django_tables2 import tables, columns

from strategy.forms import (OP_MAP, FUNC_MAP, VAR_MAP, DIM_MAP_MENU,
                            TYPE_MAP_MENU, OP_MAP_MENU)
from core.pymongo_client import get_mongo_client
from core.redis_client import get_redis_client


class BoolStrategyTable(tables.Table):
    strategy_name = columns.Column(verbose_name=_(u"策略名称"), orderable=False)
    strategy_desc = columns.Column(verbose_name=_(u"策略描述"), orderable=False)
    strategy_var = columns.Column(verbose_name=_(u"内置变量"), orderable=False)
    strategy_op = columns.Column(verbose_name=_(u"操作码"), orderable=False)
    strategy_func = columns.Column(verbose_name=_(u"内置函数"), orderable=False)
    strategy_threshold = columns.Column(verbose_name=_(u"阈值"), orderable=False)
    action = columns.TemplateColumn("""
    <a class="strategy-destroy" data-uri="{% url 'strategy:bool_strategy_destroy' %}" data-id="{{ record.uuid }}">删除</a>
    """, orderable=False, verbose_name=_(u"操作"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}

    def render_strategy_var(self, value):
        name = VAR_MAP.get(value, "")
        if name:
            return u"{0}({1})".format(name, value)
        return value

    def render_strategy_op(self, value):
        name = OP_MAP.get(value, "")
        if name:
            return u"{0}({1})".format(name, value)
        return value

    def render_strategy_func(self, value):
        name = FUNC_MAP.get(value, "")
        if name:
            return u"{0}({1})".format(name, value)
        return value


class FreqStrategyTable(tables.Table):
    strategy_name = columns.Column(verbose_name=_(u"策略名称"), orderable=False)
    strategy_desc = columns.Column(verbose_name=_(u"策略描述"), orderable=False)
    strategy_source = columns.Column(verbose_name=_(u"数据源"), orderable=False)
    strategy_body = columns.Column(verbose_name=_(u"主体名称"), orderable=False)
    strategy_time = columns.Column(verbose_name=_(u"时段(单位:秒)"), orderable=False)
    strategy_limit = columns.Column(verbose_name=_(u"最大值"), orderable=False)

    action = columns.TemplateColumn("""
    <a class="strategy-destroy" data-uri="{% url 'strategy:freq_strategy_destroy' %}" data-id="{{ record.uuid }}">删除</a>
    """, orderable=False, verbose_name=_(u"操作"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}

    def render_strategy_source(self, value):
        client = get_redis_client()
        data = client.hget("CONFIG_SOURCE_MAP", value)
        if data:
            try:
                name = json.loads(data).get('name_show', '')
            except ValueError:
                return value
            if name:
                return u"{0}({1})".format(name, value)
        return value


class MenuStrategyTable(tables.Table):
    strategy_name = columns.Column(verbose_name=_(u"策略名称"), orderable=False)
    strategy_desc = columns.Column(verbose_name=_(u"策略描述"), orderable=False)
    dimension = columns.Column(verbose_name=_(u"维度"), orderable=False)
    menu_op = columns.Column(verbose_name=_(u"操作码"), orderable=False)
    event = columns.Column(verbose_name=_(u"项目"), orderable=False)
    menu_type = columns.Column(verbose_name=_(u"名单类型"), orderable=False)
    action = columns.TemplateColumn("""
    <a class="strategy-destroy" data-uri="{% url 'strategy:menu_strategy_destroy' %}" data-id="{{ record.uuid }}">删除</a>
    """, orderable=False, verbose_name=_(u"操作"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}

    def render_menu_type(self, value):
        return TYPE_MAP_MENU.get(value, value)

    def render_menu_op(self, value):
        return OP_MAP_MENU.get(value, value)

    def render_dimension(self, value):
        return DIM_MAP_MENU.get(value, value)

    def render_event(self, value):
        db = get_mongo_client()
        res = db['menu_event'].find_one({'event_code': value}) or {}
        return res.get('event_name', value)


class UserStrategyTable(tables.Table):
    strategy_name = columns.Column(verbose_name=_(u"策略名称"), orderable=False)
    strategy_desc = columns.Column(verbose_name=_(u"策略描述"), orderable=False)
    strategy_source = columns.Column(verbose_name=_(u"数据源"), orderable=False)
    strategy_body = columns.Column(verbose_name=_(u"主体名称"), orderable=False)
    strategy_day = columns.Column(verbose_name=_(u"自然日(单位:个)"), orderable=False)
    strategy_limit = columns.Column(verbose_name=_(u"最大值"), orderable=False)

    action = columns.TemplateColumn("""
        <a class="strategy-destroy" data-uri="{% url 'strategy:user_strategy_destroy' %}" data-id="{{ record.uuid }}">删除</a>
        """, orderable=False, verbose_name=_(u"操作"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}

    def render_strategy_source(self, value):
        client = get_redis_client()
        data = client.hget("CONFIG_SOURCE_MAP", value)
        if data:
            try:
                name = json.loads(data).get('name_show', '')
            except ValueError:
                return value
            if name:
                return u"{0}({1})".format(name, value)
        return value
