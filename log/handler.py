# coding=utf8

from logging import Handler

from redis import RedisError


class RedisHandler(Handler):
    def __init__(self, conn, queue='log', retry_counts=3):
        Handler.__init__(self)
        self.conn = conn
        self.queue = queue
        assert retry_counts > 0
        self.retry_counts = retry_counts

    def emit(self, record):
        try:
            msg = self.format(record)
            for _ in range(self.retry_counts):
                try:
                    self.conn.lpush(self.queue, msg)
                    break
                except RedisError:
                    pass
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)
