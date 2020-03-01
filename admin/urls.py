from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.views.defaults import page_not_found, server_error, permission_denied


urlpatterns = [
    path(r'admin/', admin.site.urls, name='admin'),
    path(r'', include(("risk_auth.urls", "risk_auth"), namespace='risk_auth')),
    path(r'permissions/', include(("permissions.urls", "permissions"), namespace="permissions")),
    path(r'strategy/', include(("strategy.urls", "strategy"), namespace="strategy")),
    path(r'menu/', include(("menu.urls", "menu"), namespace="menus")),
    path(r'rule/', include(("rule.urls", "rule"), namespace="rule")),
    path(r'config/', include(("bk_config.urls", "config"), namespace="config")),
    path(r'log_manage/', include(("log_manage.urls", "log_manage"), namespace="log_manage")),
]

# 用于线上时应移除此部分，动静分离
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path(r'404/', page_not_found),
        path(r'500/', server_error),
        path(r'403/', permission_denied),
        path('__debug__/', include(debug_toolbar.urls)),
    ]
