# -*- coding: utf-8 -*-

from socket import gethostname
from platform import python_version

from django import get_version as get_django_version
from django.urls import reverse, resolve, Resolver404
from django.conf import settings


def serve_environment_info():
    hostname = gethostname()
    return {
        'hostname': hostname.split('.', 1)[0],
        'django_version': get_django_version(),
        'python_version': python_version(),
        'soc_version': settings.SOC_VERSION,
    }


def build_admin_sidebar(permission_uris=None):
    result = settings.SOC_SIDEBAR.to_dict(permission_uris)['value']
    return result


def build_admin_tabs(request):
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


def project_info(request):
    return {
        'deploy_env': serve_environment_info(),
        'admin_footer_links': settings.ADMIN_FOOTER_LINKS,
        'soc_sidebar': build_admin_sidebar(),
        'soc_tabs': build_admin_tabs(request),
    }
