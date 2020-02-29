import json
import time
import uuid
from datetime import datetime

from django.conf import settings

from core.redis_client import get_redis_client
from risk_models.strategy import Strategys


class RuleModel(object):

    @classmethod
    def create(self, creator_name, title, describe, status, end_time,
               strategy_confs):
        strategy_obj = Strategys()

        new_strategy_confs = []
        for name, strategy_uuids, control, custom, weight in strategy_confs:
            strategy_uuids = strategy_uuids.split(';')

            new_strategy_confs.append({
                'name': name,
                'custom': custom,
                'control': control,
                'weight': weight,
                'strategy_list': [
                    [strategy_uuid,
                     strategy_obj.get_thresholds(strategy_uuid),
                     strategy_obj.get_strategy_name(strategy_uuid)] for
                    strategy_uuid in strategy_uuids]
            })

        strategy_list = sorted(new_strategy_confs,
                               key=lambda x: int(x["weight"]),
                               reverse=True)

        rule_uuid = str(uuid.uuid4())

        payload = {
            'uuid': rule_uuid,
            'user': creator_name,
            'update_time': str(int(time.time())),
            'end_time': datetime.strftime(end_time, '%Y-%m-%d %H:%M:%S'),
            'title': title,
            'describe': describe,
            'status': status,
            'strategys': json.dumps(strategy_list)
        }

        client = get_redis_client()
        rule_id = client.incr(settings.LAST_RULE_ID_KEY)
        payload['id'] = rule_id

        rule_key = 'rule:{}'.format(rule_uuid)
        client.hmset(rule_key, payload)
        return str(rule_id), rule_uuid
