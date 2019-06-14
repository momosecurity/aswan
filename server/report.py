# coding=utf8

from .base import Response
from risk_models.source import Sources


sources = Sources(auto_fresh=True)
sources.load_sources()


def report_handler(req_body):
    source_name = req_body.get('source_name')
    if source_name is None:
        return Response(error='invalid source', ec=100)
    try:
        if not sources.check_all(source_name, req_body):
            return Response(error='invalid input', ec=101)
        else:
            if sources.write_all(source_name, req_body):
                return Response('success')
            else:
                return Response(error='database error', ec=102)
    except ValueError:
        return Response(error='invalid source', ec=100)
