# coding=utf8

from django.conf.urls import url
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required

from risk_auth.views import Home
from risk_auth.views import risk_login, risk_logout

urlpatterns = [
    url(r'^$', login_required(Home.as_view()), name='home'),
    url(r'^home/$', RedirectView.as_view(url=reverse_lazy('risk_auth:home'), permanent=True)),
    url(r'^accounts/login/$', risk_login, name="risk_login"),
    url(r'^accounts/logout/$', risk_logout, name="risk_logout"),
]
