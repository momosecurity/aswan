# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLogModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=64, verbose_name='\u7528\u6237\u540d', blank=True)),
                ('email', models.CharField(max_length=128, verbose_name='\u90ae\u7bb1', blank=True)),
                ('path', models.CharField(max_length=128, verbose_name='\u8bf7\u6c42\u5730\u5740', blank=True)),
                ('status', models.CharField(max_length=32, verbose_name='\u54cd\u5e94\u7801', blank=True)),
                ('method', models.CharField(max_length=32, verbose_name='\u8bf7\u6c42\u7c7b\u578b', blank=True)),
                ('req_body', models.TextField(verbose_name='\u8bf7\u6c42\u53c2\u6570', blank=True)),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='\u64cd\u4f5c\u65f6\u95f4')),
            ],
            options={
                'ordering': ('-time',),
                'db_table': 'user_audit_log',
                'verbose_name': '\u5ba1\u8ba1\u65e5\u5fd7',
            },
        ),
    ]
