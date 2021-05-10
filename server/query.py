# coding=utf8

from .base import Response
from risk_models.exceptions import RuleNotExistsException
from risk_models.rule import calculate_rule, Rules, AccessCount

rules = Rules(auto_refresh=True)
ac = AccessCount(auto_persist=True)


def query_handler(req_body):
    rule_id = req_body.get('rule_id')

    result, ec, error = None, 0, None
    try:
        assert rule_id
        rule_id = str(rule_id)
        control, weight = calculate_rule(rule_id, req_body, rules=rules, ac=ac)
        result = {'control': control, 'weight': weight}
    except AssertionError:
        error = 'must contain rule_id'
        ec = 100
    except RuleNotExistsException:
        error = 'rule_id does not exist or is offline'
        ec = 101

    return Response(result=result, error=error, ec=ec)
