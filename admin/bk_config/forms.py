# coding=utf8

import re
import json
from django import forms
from django.utils.translation import ugettext_lazy as _
from core.forms import BaseFilterForm, BaseForm
from core.redis_client import get_redis_client


class SourceMapForm(BaseForm):
    name_key = forms.CharField(
        min_length=2, max_length=32,
        widget=forms.TextInput(attrs={"placeholder": "配置key[字母数字下划线]"})
    )
    name_show = forms.CharField(
        min_length=2, max_length=32,
        widget=forms.TextInput(attrs={"placeholder": "配置名称[输入中文描述]"})
    )
    content = forms.CharField(widget=forms.Textarea(
        attrs={
            "rows": "8", "cols": "27",
            "placeholder": """配置内容(json格式):
{
    "user_id": "string",
    "uid": "string",
    "ip": "string"
}"""
        }))

    name_key_pattern = r"^[a-zA-Z\d_]+$"
    map_key = 'CONFIG_SOURCE_MAP'

    def clean_name_key(self):
        name_key = self.cleaned_data['name_key']
        if not re.match(self.name_key_pattern, name_key):
            raise forms.ValidationError("输入错误，包含某些特殊字符")

        client = get_redis_client()
        if client.hget(self.map_key, name_key):
            raise forms.ValidationError("该数据源已存在")

        return name_key

    def clean_content(self):
        content = self.cleaned_data['content']
        try:
            content = json.loads(content)
        except ValueError:
            raise forms.ValidationError("输入错误， json解析失败")
        if not content.keys():
            raise forms.ValidationError("这个字段是必填项")
        return content

    def save(self):
        client = get_redis_client()
        cd = self.cleaned_data
        name_key = cd['name_key']
        name_show = cd['name_show']
        content = cd['content']
        content.update(name_show=name_show)
        client.hset(self.map_key, name_key, json.dumps(content))
        return name_key


class SourceFilterForm(BaseFilterForm):
    name = forms.CharField(required=False, label=_(u"数据源名称"))
