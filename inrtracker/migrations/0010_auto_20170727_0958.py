# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-07-27 07:58
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('inrtracker', '0009_auto_20170727_0958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='hour',
            field=models.TimeField(default=datetime.datetime(2017, 7, 27, 7, 58, 42, 676058, tzinfo=utc)),
        ),
    ]
