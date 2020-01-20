# coding=utf8
import atexit
import random
from logging import Handler, getLogger

import gevent
from redis import RedisError

logger = getLogger(__name__)


def split_large_collection(collection, size):
    collection = list(collection)
    for i in range(0, len(collection), size):
        yield collection[i:i + size]


class RedisHandler(Handler):
    def __init__(self, conn, queue='log', retry_counts=3, auto_persistence=True):
        Handler.__init__(self)
        self.conn = conn
        self.queue = queue
        assert retry_counts > 0
        self.retry_counts = retry_counts
        self.auto_persistence = auto_persistence
        self.cached_logs = []
        if self.auto_persistence:
            gevent.spawn(self.auto_push)
            atexit.register(self.process_cached_log)

    def push_logs(self, *msgs):
        try:
            for _ in range(self.retry_counts):
                try:
                    self.conn.lpush(self.queue, *msgs)
                    break
                except RedisError:
                    pass
        except (KeyboardInterrupt, SystemExit):
            raise

    def process_cached_log(self):
        if not self.cached_logs:
            return

        cached_logs = self.cached_logs
        self.cached_logs = []
        logger.info('auto push log, count: {}.'.format(len(cached_logs)))
        for tmp_cached_logs in split_large_collection(cached_logs, 20):
            self.push_logs(*tmp_cached_logs)

    def emit(self, record):
        try:
            msg = self.format(record)
        except Exception:
            self.handleError(record)
            return

        if self.auto_persistence:
            self.cached_logs.append(msg)
        else:
            self.push_logs([msg])

    def auto_push(self):
        while True:
            gevent.sleep(1 + random.randint(0, 2))
            try:
                self.process_cached_log()
            except Exception:
                logger.exception('process cached log fail.')
