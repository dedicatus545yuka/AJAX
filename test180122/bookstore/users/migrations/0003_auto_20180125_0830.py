# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='recipient_phone',
            field=models.CharField(verbose_name='联系电话', max_length=11),
        ),
        migrations.AlterField(
            model_name='address',
            name='zip_code',
            field=models.CharField(verbose_name='邮政编码', max_length=6),
        ),
    ]
