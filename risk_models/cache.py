# coding=utf8
import logging
import os
import random
from collections import defaultdict

import gevent

from clients.redis_client import get_config_redis_client

logger = logging.getLogger(__name__)


class Cache(object):
    def __init__(self, scan_key, refresh_interval=300):
        self.scan_key = scan_key
        self.refresh_interval = refresh_interval

        self.__client = get_config_redis_client()
        self.__menu_maps = defaultdict(set)
        self.__in_django = "DJANGO_SETTINGS_MODULE" in os.environ
        menu_maps = self.__build_menu_maps()
        for k in menu_maps:
            self.__menu_maps[k] = menu_maps[k]
        if not self.__in_django:
            gevent.spawn(self.__refresh_menu_maps)

    def __build_menu_maps(self):
        tmp_maps = defaultdict(set)
        for key in self.__client.scan_iter(match=self.scan_key):
            key_set = self.__get_key_from_redis(key)
            if key_set:
                tmp_maps[key] = key_set
        return tmp_maps

    def __get_key_from_redis(self, key):
        key_set = set()
        for item in self.__client.sscan_iter(key):
            key_set.add(item)
        return key_set

    def __getitem__(self, item):
        if self.__in_django:
            return self.__get_key_from_redis(item)
        else:
            return self.__menu_maps.get(item, set())

    def __refresh_menu_maps(self):
        while True:
            gevent.sleep(self.refresh_interval + random.randint(1, 60))
            logger.info('start refresh %s cache', self.scan_key)
            try:
                tmp_maps = self.__build_menu_maps()
                if tmp_maps:
                    self.__menu_maps = tmp_maps
            except Exception as e:
                logger.error('refresh %s cache failed', self.scan_key,
                             exc_info=e)
            else:
                logger.info('refresh %s cache success', self.scan_key)


menu_cache = Cache(scan_key="menu:*")
