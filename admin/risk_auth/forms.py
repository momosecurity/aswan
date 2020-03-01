# coding=utf8
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm


class AuthenticationForm(BaseAuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)

    error_messages = {
        'invalid_login': _("请输入一个正确的用户名和密码，请注意他们都是区分大小写的."),
        'inactive': _("This account is inactive.")
    }
