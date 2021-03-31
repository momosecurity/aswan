# coding-utf-8

from datetime import datetime, timedelta

from www.core.utils import get_sample_str
from www.rule.models import RuleModel


def create_rule(strategy_confs, end_time=None, title=None, describe=None,
                status='on', creator_name=None):
    creator_name = creator_name or get_sample_str()
    describe = describe or get_sample_str()
    title = title or get_sample_str()
    end_time = end_time or (datetime.now() + timedelta(days=10))
    return RuleModel.create(creator_name, title, describe, status, end_time,
                            strategy_confs)
