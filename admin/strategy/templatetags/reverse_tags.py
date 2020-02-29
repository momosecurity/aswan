# coding=utf8
import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def mongo_id(value):
    """返回mongo的_id属性"""
    return value.get('_id', '')


def get_row_id(value):
    """返回mongo的_id属性"""
    return value.get('id', '')


def smart_true_false(value):
    if value and value != '0':
        return mark_safe('<i class="fa fa-check"></i>')
    else:
        return mark_safe('<i class="fa fa-close"></i>')


def jsonify(object):
    try:
        if not isinstance(object, str):
            return mark_safe(json.dumps(object))
        else:
            return object
    except (ValueError, TypeError):
        return object


def repr_str(value):
    if isinstance(value, str):
        repr_value = repr(value).lstrip("u")[1:-1]
        return repr_value
    else:
        return value


def mongo_dict_to_json(value):
    try:
        if isinstance(value, dict):
            if 'last_update' in value:
                value['last_update'] = value['last_update'].strftime("%Y-%m-%d %H:%M:%S")
            if 'expire_date' in value:
                value['expire_date'] = value['expire_date'].strftime("%Y-%m-%d %H:%M:%S")
            value['_id'] = str(value['_id'])

            json_value = json.dumps(value)
            return json_value
        else:
            return value
    except (ValueError, TypeError):
        return value


def truncatesmart(value, limit=80):
    """
    Truncates a string after a given number of chars keeping whole words.

    Usage:
        {{ string|truncatesmart }}
        {{ string|truncatesmart:50 }}
    """

    try:
        limit = int(limit)
    # invalid literal for int()
    except ValueError:
        # Fail silently.
        return value

    value = str(value)

    # Return the string itself if length is smaller or equal to the limit
    if len(value) <= limit:
        return value

    # Cut the string
    value = value[:limit]

    # Join the words and return
    return value + '...'


register.filter(jsonify)
register.filter(mongo_id)
register.filter(get_row_id)
register.filter(smart_true_false)
register.filter(repr_str)
register.filter(mongo_dict_to_json)
register.filter(truncatesmart)
