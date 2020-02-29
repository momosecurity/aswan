# -*- coding: utf-8 -*-

import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from core.forms import BaseFilterForm, BaseForm
from .permission import (
    UserPermission, GroupPermission, UriGroupPermission
)


def get_multiple_choices(perm_class):
    choices = []
    docs = perm_class.objects.all(meta_only=True)
    for doc in docs:
        pk, desc = doc.get('pk'), doc.get('desc')
        if pk is not None and desc is not None:
            choices.append((pk, desc))
    return choices


class UserPermFilterForm(BaseFilterForm):
    fullname = forms.CharField(required=False, label=_("姓名"))
    pk = forms.EmailField(required=False, label=_("email"))


class UserPermUpdateForm(BaseForm):
    FORBID_ATTR = {
        "class": "form-control", "disable": "true", "readonly": "true"
    }
    entity_id = forms.CharField(widget=forms.TextInput(attrs=FORBID_ATTR))
    fullname = forms.CharField(widget=forms.TextInput(attrs=FORBID_ATTR),
                               required=False)
    pk = forms.EmailField(widget=forms.TextInput(attrs=FORBID_ATTR))
    remark = forms.CharField(widget=forms.TextInput(), required=False)
    is_superuser = forms.BooleanField(required=False, initial='off')
    groups = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, initial=[], required=False,
    )
    permissions = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, initial=[], required=False,
    )

    INVALID_CHAR = re.compile(r'[${}/\\]')

    def __init__(self, *args, **kwargs):
        super(UserPermUpdateForm, self).__init__(*args, **kwargs)
        self.fields['groups'].choices = get_multiple_choices(GroupPermission)
        self.fields['permissions'].choices = get_multiple_choices(
            UriGroupPermission)
        self.remove_class('permissions', 'groups')

    def clean_pk(self):
        pk = self.cleaned_data['pk']
        if self.INVALID_CHAR.search(pk):
            raise forms.ValidationError('不合法的输入')
        return pk

    def clean_fullname(self):
        desc = self.cleaned_data['fullname']
        if self.INVALID_CHAR.search(desc):
            raise forms.ValidationError('不合法的输入')
        return desc

    def save(self):
        entity_id = self.cleaned_data['entity_id']
        user = UserPermission.objects.get_by_id(entity_id)
        if not user:
            return False
        user.is_superuser = self.cleaned_data['is_superuser']
        user.groups = self.cleaned_data['groups']
        user.permissions = self.cleaned_data['permissions']
        user.remark = self.cleaned_data['remark']
        return user.save()


class GroupPermUpdateForm(BaseForm):
    FORBID_ATTR = {
        "class": "form-control", "disable": "true", "readonly": "true"
    }
    entity_id = forms.CharField(widget=forms.TextInput(attrs=FORBID_ATTR),
                                required=False)
    pk = forms.CharField(widget=forms.TextInput(),
                         required=True, min_length=3, max_length=128)
    desc = forms.CharField(required=True, min_length=3, max_length=128)
    permissions = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, initial=[], required=False,
    )

    INVALID_CHAR = re.compile(r'[${}/\\]')

    def __init__(self, disable_name=True, *args, **kwargs):
        super(GroupPermUpdateForm, self).__init__(*args, **kwargs)
        if disable_name:
            self.fields['pk'].widget.attrs = self.FORBID_ATTR
        self.fields['permissions'].choices = get_multiple_choices(
            UriGroupPermission)
        self.remove_class('permissions')

    def clean_pk(self):
        pk = self.cleaned_data['pk']
        if self.INVALID_CHAR.search(pk):
            raise forms.ValidationError('不合法的输入')
        return pk

    def clean_desc(self):
        desc = self.cleaned_data['desc']
        if self.INVALID_CHAR.search(desc):
            raise forms.ValidationError('不合法的输入')
        return desc

    def save(self):
        desc = self.cleaned_data['desc']
        pk = self.cleaned_data['pk']
        permissions = self.cleaned_data['permissions']

        entity_id = self.cleaned_data.get('entity_id')
        if entity_id:
            group = GroupPermission.objects.get_by_id(entity_id)
            if not group:
                return False
            group.desc = desc
            group.permissions = permissions
        else:
            group = GroupPermission(pk, desc, permissions)
        return group.save()


class UriGroupPermUpdateForm(BaseForm):
    FORBID_ATTR = {
        "class": "form-control", "disable": "true", "readonly": "true"
    }
    entity_id = forms.CharField(widget=forms.TextInput(attrs=FORBID_ATTR),
                                required=False)
    desc = forms.CharField(required=True, min_length=3, max_length=128)
    pk = forms.CharField(widget=forms.TextInput(),
                         required=True, min_length=3, max_length=128)
    uris = forms.CharField(required=True, widget=forms.Textarea())

    VALID_URL = re.compile(r'/[a-zA-Z0-9/-_]+')
    INVALID_CHAR = re.compile(r'[${}\\]')

    def __init__(self, disable_name=True, *args, **kwargs):
        super(UriGroupPermUpdateForm, self).__init__(*args, **kwargs)
        if disable_name:
            self.fields['pk'].widget.attrs = self.FORBID_ATTR

    def clean_uris(self):
        uris = self.cleaned_data['uris']
        uris = [uri.strip() for uri in uris.split('\n')]
        for uri in uris:
            if not self.VALID_URL.match(uri) or self.INVALID_CHAR.search(uri):
                raise forms.ValidationError('uri格式错误或包含非法字符')
        return uris

    def clean_pk(self):
        pk = self.cleaned_data['pk']
        if self.INVALID_CHAR.search(pk):
            raise forms.ValidationError('不合法的输入')
        return pk

    def clean_desc(self):
        desc = self.cleaned_data['desc']
        if self.INVALID_CHAR.search(desc):
            raise forms.ValidationError('不合法的输入')
        return desc

    def save(self):
        desc = self.cleaned_data['desc']
        pk = self.cleaned_data['pk']
        uris = self.cleaned_data['uris']

        entity_id = self.cleaned_data.get('entity_id')
        if entity_id:
            uri_group = UriGroupPermission.objects.get_by_id(entity_id)
            if not uri_group:
                return False
            uri_group.desc = desc
            uri_group.uris = uris
        else:
            uri_group = UriGroupPermission(pk, desc, uris)
        return uri_group.save()
