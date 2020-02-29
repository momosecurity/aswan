import os
import sys
from pathlib import Path

from project.utils.sidebar import Menu, SubMenu, LeafMenu


#################
# Project basic #
#################
DEBUG = True
WWW_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR = WWW_DIR.parent
sys.path.append(str(PROJECT_DIR))

SECRET_KEY = '=====PLEASE_REPLACE_THIS_SECRET_KEY_IN_PRODUCTION_MODE====='

ALLOWED_HOSTS = [
    "*",
]
WSGI_APPLICATION = 'wsgi.application'
ROOT_URLCONF = 'urls'

SOC_VERSION = '2.0.0'


######################
# Databases settings #
######################
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, '../db.sqlite3'),
    }
}


##########################
# Application definition #
##########################
INSTALLED_APPS = (
    # Django contrib
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Dependencies
    'django_tables2',
    'crispy_forms',

    # Project apps
    'risk_auth',
    'permissions',
    'strategy',
    'menu',
    'rule',
    'bk_config',
    'log_manage',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'permissions.middleware.PermissionsMiddleware',
    'permissions.middleware.UserAuditMiddleware'
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [WWW_DIR / 'project' / 'templates', ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'permissions.context_processors.menu_by_perms',
                'project.context_processors.project_info',
            ],
        },
    },
]


########################
# Internationalization #
########################
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = False


################
# Static Files #
################
MEDIA_URL = '/media/'
MEDIA_ROOT = WWW_DIR / 'project' / 'media'

STATIC_URL = '/static/'
STATIC_ROOT = WWW_DIR / 'project' / 'site-static'
STATICFILES_DIRS = (
    WWW_DIR / 'project' / 'static',
)


#########################
# Risk control settings #
#########################
# 策略的签名key
STRATEGY_SIGN_KEY = 'strategy_sign'

# 保存最新的规则ID，用于生成
LAST_RULE_ID_KEY = 'last_rule_id'


risk_env = os.environ.get('RISK_ENV', 'develop')


#################
# Admin Sidebar #
#################
SOC_FOOTER_LINKS = {
    '陌陌官网': {
        '官网首页': 'http://www.immomo.com/',
        '陌陌网页版': 'https://web.immomo.com/?fr=gw_nav',
        '加入我们': 'http://www.immomo.com/jobs/join/index',
        '关于陌陌': 'http://www.immomo.com/aboutus.html'
    },
    '应急响应SRC': {
        '提交漏洞/情报': 'https://security.immomo.com/report',
        '公告': 'https://security.immomo.com/blog',
        '名人堂': 'https://security.immomo.com/fame',
        '积分兑换': 'https://security.immomo.com/shop',
    },
    '安全文档': {
        '风控文档': 'https://github.com/momosecurity/aswan/blob/master/README.md',
    },
    '陌陌安全开源': {
        'Aswan风控策略引擎': 'https://github.com/momosecurity/aswan',
        'JAVA安全SDK及编码规范': 'https://github.com/momosecurity/rhizobia_J',
        'PHP安全SDK及编码规范': 'https://github.com/momosecurity/rhizobia_P',
        'GitHub': 'https://github.com/momosecurity/'
    }
}


################
# SOC侧边栏配置 #
################
URL_DESC_MAP = {
    'menus:event_list': '名单项目管理',
    'menus:userid_list': '用户ID管理',
    'menus:ip_list': 'IP地址管理',
    'menus:uid_list': '设备号管理',
    'menus:pay_list': '支付账号管理',
    'menus:phone_list': '手机号管理',
    'strategy:menu_strategy_list': '名单型策略配置',
    'strategy:bool_strategy_list': '布尔型策略配置',
    'strategy:freq_strategy_list': '时段频控型策略配置',
    'strategy:user_strategy_list': '限用户数型策略配置',
    'rule:list': '规则配置',
    'log_manage:hit_list_detail': '拦截日志详情',
    'log_manage:audit_logs': '访问日志详情',
    'permissions:users': '用户管理',
    'permissions:groups': '组管理',
    'permissions:uri_groups': 'URL组管理',
    'config:source_list': '数据源配置'
}


###########
# 快速导航 #
###########
SOC_QUICK_NAV = {}
SOC_SIDEBAR = Menu(name="Aswan", value=[
    Menu(name="名单管理", icon="layers", value=[
        LeafMenu(name="名单项目管理", value=['menus:event_list']),
        LeafMenu(name="用户ID管理", value=['menus:userid_list']),
        LeafMenu(name="IP地址管理", value=['menus:ip_list']),
        LeafMenu(name="设备号管理", value=['menus:uid_list']),
        LeafMenu(name="支付账号管理", value=['menus:pay_list']),
        LeafMenu(name="手机号管理", value=['menus:phone_list']),
    ]),
    Menu(name="策略原子", icon="package", value=[
        LeafMenu(name="名单型策略配置", value=['strategy:menu_strategy_list']),
        LeafMenu(name="布尔型策略配置", value=['strategy:bool_strategy_list']),
        LeafMenu(name="时段频控型策略配置", value=['strategy:freq_strategy_list']),
        LeafMenu(name="限用户数型策略配置", value=['strategy:user_strategy_list']),
    ]),
    Menu(name="规则管理", icon="toggle-left", value=[
        LeafMenu(name="规则配置", value=['rule:list']),
    ]),
    Menu(name="日志管理", icon="file-text", value=[
        LeafMenu(name="拦截日志详情", value=['log_manage:hit_list_detail']),
        LeafMenu(name="访问日志详情", value=['log_manage:audit_logs']),
    ]),
    LeafMenu(name="认证和授权", icon="user-check", value=[
        'permissions:users',
        'permissions:groups',
        'permissions:uri_groups',
    ]),
    Menu(name="后台配置", icon="sliders", value=[
        LeafMenu(name="数据源配置", value=['config:source_list']),
    ]),
])
