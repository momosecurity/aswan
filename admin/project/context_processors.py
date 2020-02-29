# -*- coding: utf-8 -*-

import subprocess
from socket import gethostname
from platform import python_version

from django.core.urlresolvers import reverse, resolve, Resolver404
from django.conf import settings
from django import get_version as get_django_version


# Git信息
git_info = None

if settings.DEBUG:
    git_info = subprocess.check_output(['git', 'log', '-1'])
    git_info = git_info.decode().replace('<', '(')\
                                .replace('>', ')')\
                                .replace('\n', '<br>')


def serve_environment_info():
    hostname = gethostname()
    return {
        'hostname': hostname.split('.', 1)[0],
        'django_version': get_django_version(),
        'python_version': python_version(),
        'soc_version': settings.SOC_VERSION,
        'git_info': git_info,
        'debug': settings.DEBUG,
    }


def build_soc_sidebar(permission_uris=None):
    result = settings.SOC_SIDEBAR.to_dict(permission_uris)['value']
    return result


def build_soc_tabs(request):
    try:
        match = resolve(request.path)
    except Resolver404:
        return []

    url_name = f'{match.namespace}:{match.url_name}'
    menu = settings.SOC_SIDEBAR
    leaf_menu = menu.get_leaf_menu(url_name)
    if not leaf_menu:
        return []

    return [{
        'tab_name': settings.URL_DESC_MAP.get(item) or item,
        'path': reverse(item),
        'active': 'active' if item == url_name else '',
    } for item in leaf_menu.value]


def build_soc_quick_nav(request):
    """soc顶部导航快速链接"""

    if not request.user.is_authenticated():
        return []

    email = request.user.email
    name = email.split('@')[0]
    url_names = settings.SOC_QUICK_NAV.get(name) or []

    quick_navs = [{
        'name': settings.URL_DESC_MAP.get(item) or item,
        'url': reverse(item)
    } for item in url_names]

    return quick_navs


def project_info(request):
    return {
        'deploy_env': serve_environment_info,
        'soc_footer_links': settings.SOC_FOOTER_LINKS,
        'soc_sidebar': build_soc_sidebar(),
        'soc_tabs': build_soc_tabs(request),
        'soc_quick_nav': build_soc_quick_nav(request),
    }
