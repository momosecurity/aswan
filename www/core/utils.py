# coding: utf-8
import random
import string


def errors_to_dict(errors):
    """
    form.errors不可序列化,转成dict,序列化成json给前端
    """
    return dict(
        (k, map(unicode, v))
        for (k, v) in errors.iteritems()
    )

def get_sample_str(length=8):
    return ''.join(random.sample(string.lowercase, length))
