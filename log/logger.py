# coding=utf8

import os
import logging
import logging.config
import logging.handlers

from config import LOG_HOME
from .handler import RedisHandler
from config import HIT_LOG_QUEUE_NAME
from clients import get_log_redis_client


__all__ = ['init_log', 'hit_logger']


conn = get_log_redis_client()

if not os.path.exists(LOG_HOME):
    os.mkdir(LOG_HOME)

#  文本日志
logger_file = os.path.join(LOG_HOME, 'risk_control.log')

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'hit': {
            'format': '%(asctime)s|%(message)s',
        },
        'detail': {
            'format': '%(asctime)s|%(levelname)s|%(name)s|%(message)s',
        },
    },
    'handlers': {
        'default': {
            '()': logging.handlers.RotatingFileHandler,
            'formatter': 'detail',
            'filename': logger_file,
            'maxBytes': 1024 * 1024 * 50,
            'backupCount': 5,
        },
        'hit': {
            '()': RedisHandler,
            'formatter': 'hit',
            'conn': conn,
            'queue': HIT_LOG_QUEUE_NAME,
        },
    },
    'loggers': {
        'hit': {
            'handlers': ['hit'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['default'],
        'level': 'INFO',
    },
}

_inited = False


def init_log():
    global _inited
    if not _inited:
        logging.config.dictConfig(logging_config)
        _inited = True


hit_logger = logging.getLogger('hit')

init_log()
