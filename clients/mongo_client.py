from risk_models.lru import lru_cache_function
from pymongo import MongoClient

from config import (SOC_MONGO_HOST, MONGO_POOL_SIZE, MONGO_MAX_IDLE_TIME,
                    MONGO_MAX_WAITING_TIME, MONGO_SOCKET_TIMEOUT, MONGO_AUTH_DB, MONGO_USER, MONGO_PWD)


@lru_cache_function(max_size=1, expiration=24 * 3600)
def _get_mongo_pool():
    _POOL_TEMP = MongoClient(host=SOC_MONGO_HOST, maxPoolSize=MONGO_POOL_SIZE,
                             connect=False,
                             socketKeepAlive=True,
                             maxIdleTimeMS=MONGO_MAX_IDLE_TIME,
                             waitQueueTimeoutMS=MONGO_MAX_WAITING_TIME,
                             socketTimeoutMS=MONGO_SOCKET_TIMEOUT)
    if MONGO_USER and MONGO_PWD:
        _POOL_TEMP[MONGO_AUTH_DB].authenticate(MONGO_USER, MONGO_PWD)
    return _POOL_TEMP


def get_mongo_client(db_name=MONGO_AUTH_DB):
    pool = _get_mongo_pool()
    return pool[db_name]
