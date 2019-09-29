# -*- coding: utf-8 -*-

import datetime

from bson import ObjectId
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django_tables2 import tables, columns


class UserPermissionTable(tables.Table):
    fullname = columns.Column(verbose_name=_('姓名'), orderable=False)
    pk = columns.Column(verbose_name=_('email'), orderable=False)
    is_superuser = columns.BooleanColumn(null=False,
                                         verbose_name=_('超级管理员'),
                                         orderable=False)
    entity_id = columns.Column(verbose_name=_('初次登录时间'))
    remark = columns.Column(verbose_name=_('备注'), orderable=False)

    @classmethod
    def render_fullname(cls, record):
        url = reverse('permissions:user_update')
        html = '<a href="{}?entity_id={}">{}</a>'.format(url, record.get(
            'entity_id', ''), record.get('fullname', record['pk']))
        return format_html(html)

    @classmethod
    def render_entity_id(cls, value):
        create_time = ObjectId(value).generation_time
        # utc to local time
        create_time += datetime.timedelta(hours=8)
        return create_time.strftime('%Y-%m-%d %H:%M:%S')

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}


class GroupPermissionTable(tables.Table):
    desc = columns.Column(verbose_name=_('分组名'))
    pk = columns.Column(verbose_name=_('唯一标识'))
    entity_id = columns.Column(verbose_name=_('创建时间'))
    action = columns.TemplateColumn(str('x'), orderable=False,
                                    verbose_name=_('操作'))

    @classmethod
    def render_action(cls, record):
        url = reverse('permissions:group_update')
        html = (
            '''
            <a href="{1}?entity_id={0}"
               style="margin-right: 10px">变更权限
            </a>
            <a data-entity_id={0}
               class="perms-group-delete">删除
            </a>
            '''
        ).format(record.get('entity_id', ''), url)
        return format_html(html)

    @classmethod
    def render_desc(cls, value, record):
        url = reverse('permissions:group_update')
        html = '<a href="{}?entity_id={}">{}</a>'.format(
            url, record.get('entity_id', ''), value,
        )
        return format_html(html)

    @classmethod
    def render_entity_id(cls, value):
        return UserPermissionTable.render_entity_id(value)

    class Meta:
        attrs = {'class': 'table table-hover'}


class UriGroupPermissionTable(tables.Table):
    desc = columns.Column(verbose_name=_('uri组名称'))
    pk = columns.Column(verbose_name=_('唯一标识'))
    uris = columns.Column(verbose_name=_('uri列表'))
    entity_id = columns.Column(verbose_name=_('创建时间'))
    action = columns.TemplateColumn(str('x'), orderable=False,
                                    verbose_name=_('操作'))

    @classmethod
    def render_action(cls, record):
        url = reverse('permissions:uri_group_update')
        html = (
            '''
            <a href="{1}?entity_id={0}"
               style="margin-right: 10px">变更权限
            </a>
            <a data-entity_id={0}
               class="perms-uri-group-delete">删除
            </a>
            '''
        ).format(record.get('entity_id', ''), url)
        return format_html(html)

    @classmethod
    def render_desc(cls, value, record):
        url = reverse('permissions:uri_group_update')
        html = '<a href="{}?entity_id={}">{}</a>'.format(
            url, record.get('entity_id', ''), value,
        )
        return format_html(html)

    @classmethod
    def render_uris(cls, record):
        html = (
            '<pre>{}</pre>'.format('\n'.join(record['uris']))
        )
        return format_html(html)

    @classmethod
    def render_entity_id(cls, value):
        return UserPermissionTable.render_entity_id(value)

    class Meta:
        attrs = {'class': 'table table-hover'}
