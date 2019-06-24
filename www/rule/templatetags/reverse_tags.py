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


def jsonify(obj):
    if not isinstance(obj, str):
        try:
            json_str = mark_safe(json.dumps(obj))
        except:
            json_str = obj
        return json_str
    return obj


def repr_str(value):
    if isinstance(value, str):
        repr_value = repr(value).lstrip("u")[1:-1]
        return repr_value
    else:
        return value


def mongo_dict_to_json(value):
    if isinstance(value, dict):
        value['_id'] = str(value['_id'])

        keys = ['last_update', 'expire_date']
        for key in keys:
            if key in value:
                value[key] = value[key].strftime('%Y-%m-%d %H:%M:%S')
        try:
            json_str = json.dumps(value)
        except:
            json_str = value
        return json_str
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

    # Make sure it's unicode
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
