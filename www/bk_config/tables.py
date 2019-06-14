# coding=utf8

from django.utils.translation import ugettext_lazy as _
from django_tables2 import tables, columns


class ConfigSourceTable(tables.Table):
    name_key = columns.Column(verbose_name=_(u"配置名称key"), orderable=False)
    name_show = columns.Column(verbose_name=_(u"配置名称"), orderable=False)
    content = columns.Column(verbose_name=_(u"配置内容"), orderable=False)
    action = columns.TemplateColumn("""
        {% load reverse_tags %}
        <a class="source-destroy" data-uri="{% url 'config:source_destroy' %}"
           data-name_key="{{ record.name_key }}">删除
        </a>
        """, orderable=False, verbose_name=_(u"操作"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}
