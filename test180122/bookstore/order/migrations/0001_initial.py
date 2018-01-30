# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
        ('users', '0003_auto_20180125_0830'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('is_delete', models.BooleanField(verbose_name='逻辑删除标志', default=False)),
                ('create_time', models.DateTimeField(verbose_name='创建的时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新的时间', auto_now=True)),
                ('count', models.IntegerField(verbose_name='商品数量', default=1)),
                ('price', models.DecimalField(verbose_name='商品价格', max_digits=10, decimal_places=2)),
                ('books', models.ForeignKey(verbose_name='订单商品', to='books.Books')),
            ],
            options={
                'db_table': 's_order_books',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('is_delete', models.BooleanField(verbose_name='逻辑删除标志', default=False)),
                ('create_time', models.DateTimeField(verbose_name='创建的时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新的时间', auto_now=True)),
                ('order_id', models.CharField(verbose_name='订单编号', primary_key=True, max_length=64, serialize=False)),
                ('total_count', models.IntegerField(verbose_name='商品总数', default=1)),
                ('total_price', models.DecimalField(verbose_name='商品总价', max_digits=10, decimal_places=2)),
                ('transit_price', models.DecimalField(verbose_name='订单运费', max_digits=10, decimal_places=2)),
                ('pay_method', models.SmallIntegerField(verbose_name='支付方式', default=1, choices=[(1, '货到付款'), (2, '支付宝付款'), (3, '微信付款'), (4, '银联卡付款')])),
                ('status', models.SmallIntegerField(verbose_name='订单状态', default=1, choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')])),
                ('trade_id', models.CharField(verbose_name='支付编号', max_length=100, unique=True, blank=True, null=True)),
                ('addr', models.ForeignKey(verbose_name='用户地址', to='users.Address')),
                ('passport', models.ForeignKey(verbose_name='用户信息', to='users.Passport')),
            ],
            options={
                'db_table': 's_order_info',
            },
        ),
        migrations.AddField(
            model_name='ordergoods',
            name='order',
            field=models.ForeignKey(verbose_name='所属订单', to='order.OrderInfo'),
        ),
    ]
