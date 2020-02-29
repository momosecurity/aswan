# coding=utf8

from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django_tables2 import tables, columns


class RulesTable(tables.Table):
    id = columns.Column(verbose_name=_(u"规则ID"), orderable=False)
    title = columns.Column(verbose_name=_(u"规则名称"), orderable=False)
    status = columns.Column(verbose_name=_(u"状态"), orderable=False)
    update_time = columns.Column(verbose_name=_(u"更新时间"), orderable=False)
    user = columns.Column(verbose_name=_(u"更新人"), orderable=False)
    action = columns.TemplateColumn("""
    <span class="action-button">
        <a class="rules-on" data-uri="{% url 'rule:change' %}" data-id="{{ record.uuid }}" data-title="{{ record.title }}" data-status="{{ record.status }}">启用</a>
    </span>
    <span class="action-button">
        <a class="rules-off" data-uri="{% url 'rule:change' %}" data-id="{{ record.uuid }}" data-title="{{ record.title }}" data-status="{{ record.status }}">停用</a>
    </span>
    <span class="action-button">
        <a class="rules-detail" data-uri="{% url 'rule:detail' %}" data-id="{{ record.uuid }}" >详情</a>
    </span>
    <span class="action-button">
        <a class="rules-edit" data-uri="{% url 'rule:edit' %}" data-id="{{ record.uuid }}" >编辑</a>
    </span>
    """, orderable=False, verbose_name=_(u"操作"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}

    def render_update_time(self, value):
        return datetime.fromtimestamp(int(value))

    def render_status(self, value):
        return u"启用" if value == 'on' else u"停用"
