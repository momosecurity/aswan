# coding=utf8
import re
import json
import uuid
import datetime

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from core.pymongo_client import get_mongo_client
from core.forms import BaseFilterForm, BaseForm
from core.redis_client import get_redis_client
from risk_models.menu import build_redis_key

# 查询时有全部名单
MENU_TYPE_CHOICES = (
    (u'', u'全部名单'),
    (u'black', u'黑名单'),
    (u'white', u'白名单'),
    (u'gray', u'灰名单')
)

MENU_STATUS_CHOICES = (
    (u'有效', u'有效'),
    (u'全部', u'全部'),
    (u'无效', u'无效')
)

# 新增时没有全部名单
MENU_TYPE_CHOICES_ADD_CHOICES = MENU_TYPE_CHOICES[1:]

MENU_TYPE_NAME_MAP = dict(MENU_TYPE_CHOICES_ADD_CHOICES)

DIMENSION_NAME_MAP = {
    "user_id": u"用户ID",
    "ip": u'IP地址',
    "phone": u"手机号",
    "uid": u"设备号",
    "pay": u"支付账号"
}


class MenuEventCreateForm(BaseForm):
    event_name = forms.CharField()

    def clean_event_name(self):
        db = get_mongo_client()
        event_name = self.cleaned_data['event_name'].strip()
        res = db.menu_event.find_one({'event_name': event_name})
        if res:
            raise forms.ValidationError(u"该项目名称已存在")
        return event_name

    def save(self, *args, **kwargs):
        db = get_mongo_client()
        cd = self.cleaned_data
        event_code = str(uuid.uuid4())
        pay_load = dict(
            event_code=event_code,
            event_name=cd['event_name']
        )
        db.menu_event.insert_one(pay_load)
        return event_code


class MenuCreateForm(BaseForm):
    value = forms.CharField(widget=forms.Textarea(
        attrs={"placeholder": "用户ID[批量添加时请以回车键隔开]", "rows": "5"}))
    dimension = forms.CharField(required=False, widget=forms.HiddenInput,
                                label=_(u'名单维度'))
    menu_type = forms.ChoiceField(label=_(u"名单类型"),
                                  choices=MENU_TYPE_CHOICES_ADD_CHOICES)
    event_code = forms.ChoiceField(label=_(u"项目"))
    end_time = forms.DateTimeField(widget=forms.TextInput(
        attrs={"placeholder": "结束时间", "class": "form-control datetime"}))
    menu_desc = forms.CharField(required=False, widget=forms.Textarea(
        attrs={"placeholder": "备注[填写增加该批数据的原因]", "rows": "5"}))

    def __init__(self, *args, **kwargs):
        super(MenuCreateForm, self).__init__(*args, **kwargs)
        self.fields['event_code'].choices = self._build_event_choices()

    @classmethod
    def _build_event_choices(cls):
        db = get_mongo_client()
        choices = [(x["event_code"], x["event_name"]) for x in
                   db['menu_event'].find({}, projection={'_id': False,
                                                         'event_code': True,
                                                         'event_name': True})]
        return choices

    def clean_value(self):
        value = self.cleaned_data['value']
        value_list = list(set(value.split()))
        try:
            json.dumps(value_list)
        except ValueError:
            raise forms.ValidationError(u"输入非法")
        if not value_list:
            raise forms.ValidationError(u"该字段是必填项。")
        return value_list

    def clean_end_time(self):
        end_time = self.cleaned_data['end_time']
        if end_time <= timezone.now():
            raise forms.ValidationError(_(u"结束时间应大于当前时间"))
        return end_time

    def _check_regex(self, values, regex):
        errors = []
        for item in values:
            if not re.match(regex, item):
                errors.append(item)
        if errors:
            msg = ', '.join(errors)
            msg = u'输入非法: {}'.format(msg)
            self.errors['value'] = [msg]

    def clean(self):
        cd = self.cleaned_data
        dimension = cd['dimension']
        values = cd['value']

        if dimension == "phone":
            self._check_regex(values, r'^1\d{10}$')
        elif dimension == 'ip':
            self._check_regex(
                values,
                r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$'
            )
        return cd

    def save(self, *args, **kwargs):
        """新增时，若存在维度值+项目+名单类型相同情况，则update为新增值"""
        cd = self.cleaned_data
        value_list = cd['value']
        chinese_name = self.request.user.username
        error_datas = []
        end_time = cd['end_time'].replace(tzinfo=None)

        db = get_mongo_client()
        redis_client = get_redis_client()
        for value in value_list:
            payload = dict(
                end_time=end_time,
                menu_desc=cd['menu_desc'],
                menu_status=u"有效",
                create_time=datetime.datetime.now(),
                creator=chinese_name
            )

            value = value.strip()
            dimension = cd['dimension']
            menu_type = cd['menu_type']
            event_code = cd.get('event_code')

            condition = dict(value=value,
                             event_code=event_code,
                             menu_type=menu_type,
                             dimension=dimension
                             )
            res = db.menus.find_one(condition)

            try:
                if not res:
                    payload.update(condition)
                    db.menus.insert_one(payload)
                else:
                    db.menus.update_one({"_id": res.get("_id", '')},
                                        {"$set": payload})

                #  同时写redis
                redis_key = build_redis_key(event_code, dimension,
                                            menu_type)
                if redis_key:
                    redis_client.sadd(redis_key, value)

            except Exception:
                error_datas.append(value)

        return error_datas


class MenuFilterForm(BaseFilterForm):
    filter_event_code = forms.ChoiceField(label=_(u"项目类型"), required=False)
    filter_menu_type = forms.ChoiceField(label=_(u"名单类型"), choices=MENU_TYPE_CHOICES, required=False)
    filter_value = forms.CharField(label=_(u"值"), required=False)
    filter_menu_status = forms.ChoiceField(choices=MENU_STATUS_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        self.dimension = kwargs.pop("dimension", None)
        super(MenuFilterForm, self).__init__(*args, **kwargs)
        self.fields['filter_event_code'].choices = self._build_event_choices()

        placeholder = DIMENSION_NAME_MAP.get(self.dimension, u'未知')
        self.fields['filter_value'].widget.attrs["placeholder"] = _(
            placeholder)

    @classmethod
    def _build_event_choices(cls):
        db = get_mongo_client()
        choices = [(x["event_code"], x["event_name"]) for x in
                   db['menu_event'].find({}, projection={'_id': False,
                                                         'event_code': True,
                                                         'event_name': True})]
        choices.insert(0, ('', u"全部项目"))
        return choices
