# coding=utf8
import json
from core.redis_client import get_redis_client

client = get_redis_client()
__all__ = ["get_source_largest_period"]


def _get_stategy_largest_period(strategy_type):
    """
    获取strategy_type类型的策略最大时长
    """
    # 1.在数据源和主体名称一致时，扫描strategy数据并获取最大时间段
    uuid_source_body = {}
    strategys = {}
    for strategy_key in client.scan_iter(match=strategy_type + ":*"):
        strategy_data = client.hgetall(strategy_key)
        uuid = strategy_key.split(":")[-1]
        source = strategy_data.get('strategy_source', '')
        body = strategy_data.get('strategy_body', '')
        uuid_source_body[uuid] = [source, body]
        period = strategy_data.get("strategy_time") or strategy_data.get("strategy_day")
        if period is None:
            continue
        key = "|".join(uuid_source_body[uuid])
        strategys.setdefault(key, set()).add(int(period))

    strategys_max = {}
    for key in strategys:
        strategys_max[key] = max(strategys[key])

    # 2.扫描阈值编辑数据,并获取最大时间段
    threshold_edit_max = {}
    for rule_key in client.scan_iter("rule:*"):
        rule_data = client.hgetall(rule_key)
        strategys_ = json.loads(rule_data.get("strategys"))
        for strategy_data in strategys_:
            strategy_list = strategy_data.get("strategy_list")
            for strategy in strategy_list:
                uuid, thresholds = strategy[0], strategy[1]
                if uuid in uuid_source_body:
                    key = "|".join(uuid_source_body[uuid])
                    if key in threshold_edit_max:
                        if threshold_edit_max[key] < int(thresholds[0]):
                            threshold_edit_max[key] = int(thresholds[0])
                    else:
                        threshold_edit_max[key] = int(thresholds[0])
    # 3.选取两者中最大值
    for k, v in strategys_max.items():
        if k not in threshold_edit_max:
            continue
        if strategys_max[k] < threshold_edit_max[k]:
            strategys_max[k] = threshold_edit_max[k]
    return strategys_max


def get_source_largest_period():
    """
    return: 返回各数据源的最大时长,单位：s
    """
    strategy_period = _get_stategy_largest_period("freq_strategy")
    daily_strategy_period = _get_stategy_largest_period("daily_strategy")

    for k in daily_strategy_period:
        daily_strategy_period[k] = daily_strategy_period[k] * 24 * 3600
        if k in strategy_period:
            if strategy_period[k] < daily_strategy_period[k]:
                strategy_period[k] = daily_strategy_period[k]
        else:
            strategy_period[k] = daily_strategy_period[k]
    return strategy_period


if __name__ == "__main__":
    print(get_source_largest_period())
