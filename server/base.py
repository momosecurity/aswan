# coding=utf8

import json


class Response(object):
    def __init__(self, result=None, error=None, ec=0):
        assert (result is not None) or (error is not None)
        self.result = result
        self.error = error
        self.ec = ec

    def __repr__(self):
        if self.error is not None:
            res = {'error': self.error, 'ec': self.ec}
        else:
            res = {'result': self.result, 'ec': 0}
        return json.dumps(res)
