import pymysql

from config import LOG_MYSQL_CONFIG


__all__ = ['get_log_mysql_client']


def get_log_mysql_client():
    return pymysql.connect(**LOG_MYSQL_CONFIG)
