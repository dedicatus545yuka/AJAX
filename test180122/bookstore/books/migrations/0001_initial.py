# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Books',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('is_delete', models.BooleanField(verbose_name='逻辑删除标志', default=False)),
                ('create_time', models.DateTimeField(verbose_name='创建的时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新的时间', auto_now=True)),
                ('type_id', models.SmallIntegerField(verbose_name='商品种类', default=1, choices=[(1, 'python'), (2, 'javascript'), (3, '算法'), (4, '机器学习'), (5, '操作系统'), (6, '数据库')])),
                ('status', models.SmallIntegerField(verbose_name='商品状态', default=1, choices=[(0, '下线'), (1, '上线')])),
                ('name', models.CharField(verbose_name='商品名称', max_length=20)),
                ('desc', models.CharField(verbose_name='商品简介', max_length=128)),
                ('price', models.DecimalField(verbose_name='商品价格', max_digits=10, decimal_places=2)),
                ('unite', models.CharField(verbose_name='商品单位', max_length=20)),
                ('stock', models.IntegerField(verbose_name='商品库存', default=1)),
                ('sales', models.IntegerField(verbose_name='商品销量', default=0)),
                ('detail', tinymce.models.HTMLField(verbose_name='商品详情')),
                ('image', models.ImageField(verbose_name='商品图片', upload_to='books')),
            ],
            options={
                'db_table': 's_books',
            },
        ),
    ]
