# coding: utf8
from django.template.defaultfilters import truncatechars
from django.utils.safestring import mark_safe
from django_tables2.columns import Column


class TruncateColumn(Column):

    def __init__(self, *args, **kwargs):
        self.truncate_limit = kwargs.pop('truncate_limit', 25)
        super(TruncateColumn, self).__init__(*args, **kwargs)

    def render(self, value):
        if isinstance(value, str) and len(value) > self.truncate_limit:
            value = u'<span title="{0}">{1}</span>'.format(value,
                                                           truncatechars(value, self.truncate_limit))
            return mark_safe(value)
        return value
