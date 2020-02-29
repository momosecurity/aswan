# coding=utf8

import json

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from core.forms import BaseFilterForm, BaseForm
from risk_models.strategy import Strategys
from risk_models.rule import Rules
from rule.models import RuleModel

STATUS_CHOICES = (
    ('on', u"启用"),
    ('off', u"停用"),
)
CONTROL_CHOICES = (
    ('', u"管控原子选择"),
    ('pass', u"直接通过"),
    ('deny', u"拒绝"),
    ('log', u"记录日志"),
    ('message', u"短信验证"),
    ('picture', u"图片验证"),
    ('number', u"数字验证"),
    ('verify', u"审核"),
)
CONTROL_MAP = {
    k: v for k, v in CONTROL_CHOICES if k
}


class RulesForm(BaseForm):
    title = forms.CharField(label=_(u"规则名称"))
    describe = forms.CharField(required=False, label=_(u"规则描述"),
                               widget=forms.Textarea)
    status = forms.ChoiceField(label=_(u"状态"), choices=STATUS_CHOICES)
    end_time = forms.DateTimeField()
    strategy = forms.ChoiceField(label=_("策略原子"), required=False)
    control = forms.ChoiceField(label=_("管控原子"), choices=CONTROL_CHOICES,
                                required=False)
    custom = forms.CharField(label=_(u"客服话术"), required=False,
                             widget=forms.Textarea(
                                 attrs={'placeholder': u'客服话术',
                                        'data-autoresize': '',
                                        'rows': '1',
                                        'cols': 'auto'}))
    strategys = forms.CharField(required=True)
    controls = forms.CharField(required=True)
    customs = forms.CharField()
    names = forms.CharField(required=True)
    weights = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(RulesForm, self).__init__(*args, **kwargs)
        strategy_choices = self._get_all_strategys()
        self.fields['strategy'].choices = strategy_choices
        self.strategy_names = strategy_choices

    @classmethod
    def _get_all_strategys(cls):
        return Strategys().get_all_strategy_uuid_and_name()

    def clean_end_time(self):
        end_time = self.cleaned_data['end_time']
        if end_time <= timezone.now():
            raise forms.ValidationError(_(u"结束时间应大于当前时间"))
        return end_time

    def clean_weights(self):
        weights = self.cleaned_data['weights']
        seps = weights.split(',')
        for num in seps:
            if not num.isdigit():
                raise forms.ValidationError(_(u"权重值不是数字"))
        return weights

    def _check_names(self, names, choices, sep=None):
        valid_names = set()
        for english, chinese in choices:
            if english:
                valid_names.add(english)
        if sep:
            all_names = []
            for name in names:
                for e in name.split(sep):
                    all_names.append(e)
            names = all_names
        return all([name in valid_names for name in names])

    def clean(self):
        cd = super(RulesForm, self).clean()

        # 已经有问题的话，就不继续校验了
        if self.errors:
            return cd

        strategys_list = cd['strategys'].split(',')
        controls = cd['controls'].split(',')
        customs = cd.get('customs', '').split(':::')
        names = cd['names'].split(':::')
        if not len(strategys_list) == len(controls) == len(customs) == len(
                names):
            self.errors['customs'] = [u'策略原子组名、策略原子、管控原子、客服话术不匹配']
        if not self._check_names(strategys_list, self._get_all_strategys(),
                                 sep=';'):
            self.errors['strategys'] = [u'非法策略原子名']
        if not self._check_names(controls, CONTROL_CHOICES):
            self.errors['controls'] = [u'非法管控原子名']
        strategy_uuids = []
        for strategy in strategys_list:
            item = strategy.split(';')
            item.sort()
            strategy_uuids.append("".join(item))
        if len(set(strategy_uuids)) < len(strategy_uuids):
            self.errors['strategys'] = [u'策略原子有重复']
        return cd

    def save(self, *args, **kwargs):
        cd = self.cleaned_data

        names = cd['names'].split(':::')
        controls = cd['controls'].split(',')
        strategys = cd['strategys'].split(',')
        customs = cd.get('customs', '').split(':::')
        weights = [int(x) for x in cd['weights'].split(',')]

        return RuleModel.create(creator_name=self.request.user.username,
                                title=cd['title'],
                                describe=cd['describe'], status=cd['status'],
                                end_time=cd['end_time'],
                                strategy_confs=zip(names, strategys, controls,
                                                   customs,
                                                   weights))


class RulesTestForm(BaseForm):
    req_body = forms.CharField(widget=forms.Textarea, label=_(u"请求体"))
    rule = forms.ChoiceField(label=_(u"规则名称"), widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super(RulesTestForm, self).__init__(*args, **kwargs)
        self.fields['rule'].choices = self._build_rule_choices()

    @classmethod
    def _build_rule_choices(cls):
        return Rules().get_all_rule_uuid_and_name()

    def clean_req_body(self):
        req_body = self.cleaned_data.get('req_body', '')
        try:
            req_body = json.loads(req_body)
        except ValueError:
            raise forms.ValidationError(u"请求体不是合法json格式")
        return req_body


class RulesFilterForm(BaseFilterForm):
    status = forms.ChoiceField(label=_(u"状态"),
                               choices=(('', '所有状态'),) + STATUS_CHOICES,
                               required=False)
    rule_name = forms.CharField(label=_(u"规则名称(可模糊查询)"), required=False)
