# coding=utf-8

from django.db import models
from django.db.models import Manager
from django.db.models.base import ModelBase
from django.utils.translation import ugettext_lazy as _


class AuditLogModel(models.Model):
    username = models.CharField(verbose_name=_(u"用户名"), max_length=64,
                                blank=True)
    email = models.CharField(verbose_name=_(u"邮箱"), max_length=128, blank=True)
    path = models.CharField(verbose_name=_(u"请求地址"), max_length=128,
                            blank=True)
    status = models.CharField(verbose_name=_(u"响应码"), max_length=32,
                              blank=True)
    method = models.CharField(verbose_name=_(u"请求类型"), max_length=32,
                              blank=True)
    req_body = models.TextField(verbose_name=_(u"请求参数"), blank=True)
    time = models.DateTimeField(verbose_name=_(u'操作时间'), auto_now_add=True)

    class Meta:
        db_table = "user_audit_log"
        ordering = ('-time',)
        verbose_name = _(u'审计日志')

    def __unicode__(self):
        return self.username

    objects = Manager()


def get_hit_log_model(db_table):
    class CustomMetaClass(ModelBase):
        def __new__(cls, name, bases, attrs):
            model = super(CustomMetaClass, cls).__new__(cls, name, bases,
                                                        attrs)
            model._meta.db_table = db_table
            return model

    class HitLogModel(models.Model, metaclass=CustomMetaClass):
        time = models.DateTimeField(verbose_name=_(u'命中时间'))
        rule_id = models.IntegerField(verbose_name=_(u'规则ID'))
        user_id = models.IntegerField(verbose_name=_(u'命中用户'))
        kwargs = models.TextField(max_length=128, verbose_name=_(u'扩展参数'))
        req_body = models.TextField(max_length=512, verbose_name=_(u'请求参数'))
        control = models.CharField(max_length=16, verbose_name=_(u'管控原子'))
        custom = models.CharField(max_length=50, verbose_name=_(u'策略组解释'))
        group_name = models.CharField(max_length=256,
                                      verbose_name=_(u'策略原子组名称'))
        group_uuid = models.CharField(max_length=36,
                                      verbose_name=_(u'策略原子组UUID'))
        hit_number = models.PositiveSmallIntegerField(verbose_name=_(u'命中次序'))

        objects = Manager()

        class Meta:
            managed = False
            index_together = (
                ('time',),
                ('user_id',),
            )

    return HitLogModel
