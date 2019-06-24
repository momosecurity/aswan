# coding=utf8

import importlib

import os

# 日志输出目录
LOG_HOME = './output'

# 命中日志队列名
HIT_LOG_QUEUE_NAME = 'hit_log_queue'

# 服务配置项
RISK_SERVER_HOST = '127.0.0.1'
RISK_SERVER_PORT = 50000

#  存储sourcemap的redis key
REDIS_SOURCE_MAP = 'CONFIG_SOURCE_MAP'

# mongodb
MONGO_POOL_SIZE = 20  # one additional to monitoring the server’s state
MONGO_MAX_IDLE_TIME = 1 * 60 * 1000  # 最大空闲时长1分钟
MONGO_SOCKET_TIMEOUT = 1 * 1000  # socket超时, 1秒
MONGO_MAX_WAITING_TIME = 100  # 最大等待时间,100毫秒
MONGO_READ_PREFERENCE = "secondaryPreferred"

MONGO_AUTH_DB = "risk_control"
MONGO_USER = "risk_control_user"
MONGO_PWD = "risk_control_pwd"

risk_env = os.environ.get('RISK_ENV', 'develop')

# 若配置文件不存在，直接无法启动
try:
    importlib.import_module('.' + risk_env, 'config')
    exec('from config.{risk_env} import *'.format(risk_env=risk_env))
except Exception:
    raise AssertionError(
        'The project should set correct RISK_ENV environment var.')
