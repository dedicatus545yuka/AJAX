# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('is_delete', models.BooleanField(verbose_name='逻辑删除标志', default=False)),
                ('create_time', models.DateTimeField(verbose_name='创建的时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新的时间', auto_now=True)),
                ('recipient_name', models.CharField(verbose_name='收件人', max_length=20)),
                ('recipient_addr', models.CharField(verbose_name='收件地址', max_length=256)),
                ('zip_code', models.IntegerField(verbose_name='邮政编码', max_length=6)),
                ('recipient_phone', models.IntegerField(verbose_name='联系电话', max_length=11)),
                ('is_default', models.BooleanField(verbose_name='是否默认', default=False)),
                ('passport', models.ForeignKey(verbose_name='账户', to='users.Passport')),
            ],
            options={
                'db_table': 's_user_address',
            },
        ),
    ]