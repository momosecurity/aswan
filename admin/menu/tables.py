# coding=utf8
from django.utils.translation import ugettext_lazy as _
from django_tables2 import tables, columns
from core.pymongo_client import get_mongo_client
from core.columns import TruncateColumn
from menu.forms import MENU_TYPE_NAME_MAP


class EventTable(tables.Table):
    event_name = columns.Column(verbose_name=_(u"项目名称"))
    action = columns.TemplateColumn("""
    <a class="event-destroy" data-uri="{% url 'menus:event_destroy' %}" data-id="{{ record.event_code }}">删除</a>
    """, orderable=False, verbose_name=_(u"操作"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}


class BaseMenuTable(tables.Table):
    check_all = columns.TemplateColumn("""
        {% load reverse_tags %}
        <input class="menu-item" data-id="{{ record|mongo_id }}" type="checkbox" />
        """, orderable=False, verbose_name="")
    value = columns.Column(verbose_name=_(u"值"))
    event_code = columns.Column(verbose_name=_(u"项目"))
    menu_type = columns.Column(verbose_name=_(u"名单类型"))
    menu_status = columns.Column(verbose_name=_(u"状态"))
    menu_desc = TruncateColumn(verbose_name=_(u"备注"))
    end_time = columns.DateTimeColumn(format="Y-m-d H:i:s", verbose_name=_(u"结束时间"))
    create_time = columns.DateTimeColumn(format="Y-m-d H:i:s", verbose_name=_(u"更新时间"))
    creator = columns.Column(verbose_name=_(u"操作人"))

    def __init__(self, *args, **kwargs):
        super(BaseMenuTable, self).__init__(*args, **kwargs)
        self.deletable = True

    def render_menu_type(self, value):
        return MENU_TYPE_NAME_MAP.get(value, value)

    def render_event_code(self, value):
        db = get_mongo_client()
        res = db.menu_event.find_one({'event_code': value})
        if not res:
            return value
        return res.get('event_name', value)


class UseridTable(BaseMenuTable):
    value = columns.Column(verbose_name=_(u"用户ID"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}


class IPTable(BaseMenuTable):
    value = columns.Column(verbose_name=_(u"IP地址"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}


class UidTable(BaseMenuTable):
    value = columns.Column(verbose_name=_(u"设备号"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}


class PayTable(BaseMenuTable):
    value = columns.Column(verbose_name=_(u"支付账号"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}


class PhoneTable(BaseMenuTable):
    value = columns.Column(verbose_name=_(u"手机号"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}
