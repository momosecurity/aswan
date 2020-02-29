# coding=utf8
from datetime import datetime, timedelta

from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, HTML, Reset, Field


class FormBaseMixin(object):
    """insert/update html base form"""

    def __init__(self, *args, **kwargs):

        super(FormBaseMixin, self).__init__(*args, **kwargs)

        self.error_text_inline = kwargs.get("error_text_inline", True)
        self.form_action = kwargs.get("form_action", ".")
        # css class属性值,可以style写法
        self.form_class = kwargs.get("form_class", "")
        self.form_inputs = kwargs.get("form_inputs", [])
        self.form_method = kwargs.get("form_method", "get")

    def get_form_method(self):
        return self.form_method

    def get_form_action(self):
        return self.form_action

    def get_form_class(self):
        return self.form_class

    def get_form_inputs(self):
        return self.form_inputs

    def get_layout(self, helper):
        return helper.build_default_layout(self)

    @property
    def helper(self):
        if not hasattr(self, '_helper'):
            self._helper = FormHelper()
            self._helper.error_text_inline = self.error_text_inline
            self._helper.form_action = self.get_form_action()
            self._helper.form_class = self.get_form_class()
            self._helper.form_method = self.get_form_method()

            for _input in self.get_form_inputs():
                self._helper.add_input(_input)

            self._helper.layout = self.get_layout(self._helper)

        return self._helper


class BaseForm(FormBaseMixin, forms.Form):
    i18n_fields = []

    form_class = 'form-horizontal'
    form_inputs = [Submit('submit', _(u'保存')),
                   Reset('reset', _(u'重置'))]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BaseForm, self).__init__(*args, **kwargs)

        lang = self.get_lang()
        if lang:
            for field in self.i18n_fields:
                self.fields.pop('%s_%s' % (field, lang), None)

        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

    def remove_class(self, *field_names):
        for field_name in field_names:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.pop('class')

    def is_edit(self):
        return self.instance.pk is not None

    def get_lang(self):
        return getattr(self.request, 'LANGUAGE_CODE', '').replace('-', '_')


class BaseFilterForm(FormBaseMixin, forms.Form):
    """filter search base form"""

    def __init__(self, *args, **kwargs):
        super(BaseFilterForm, self).__init__(*args, **kwargs)
        self.form_class = 'form-inline'
        self.form_method = "get"
        for field in self.fields:
            self.fields[field].help_text = False
            css_class = self.fields[field].widget.attrs.get("class", "")
            self.fields[field].widget.attrs[
                "class"] = "form-control {0}".format(css_class)
            self.fields[field].widget.attrs["placeholder"] = self.fields[
                field].label
            self.fields[field].label = False
        self.keys = self.fields.keys()

    def get_layout(self, helper):
        items = [Field(x, wrapper_class="form-group") for x in self.fields]
        action = FormActions(Submit('submit', _(u'查询')),
                             css_class="form-group")
        items.append(action)
        layout = Layout(*items)
        return layout


class BaseTimeFilterForm(forms.Form):
    time_start = forms.CharField(label=_(u"开始时间"), required=False)
    time_end = forms.CharField(label=_(u"结束时间"), required=False)

    left_sub_days = 3

    def clean_time_start(self, ):
        time_start_str = self.cleaned_data.get('time_start', '')
        time_start = None
        if time_start_str:
            try:
                time_start = datetime.strptime(time_start_str,
                                               '%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                pass
        if not time_start:
            time_start = datetime.now() - timedelta(days=self.left_sub_days)
        return time_start

    def clean_time_end(self):
        time_end_str = self.cleaned_data.get('time_end', '')
        time_end = None
        if time_end_str:
            try:
                time_end = datetime.strptime(time_end_str,
                                             '%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                pass
        if not time_end:
            time_end = datetime.now()
        return time_end
