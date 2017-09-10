# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-07-15 10:15
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('drugid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=40)),
                ('activesub', models.IntegerField()),
                ('units', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='INR',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('INRValue', models.DecimalField(decimal_places=2, max_digits=4)),
                ('testdate', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TakenDrugs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('takendate', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('dose', models.DecimalField(decimal_places=2, max_digits=4)),
                ('drugid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inrtracker.Drug')),
            ],
        ),
        migrations.CreateModel(
            name='test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.CharField(max_length=60)),
                ('testtype', models.CharField(max_length=30)),
                ('hour', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UsedDrugs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('useddose', models.CharField(max_length=40)),
                ('userlogin', models.CharField(default='', max_length=20)),
                ('drugid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inrtracker.Drug')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('name', models.CharField(max_length=20)),
                ('surname', models.CharField(max_length=40)),
                ('login', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=20)),
                ('wantedinr', models.DecimalField(decimal_places=2, max_digits=4)),
            ],
        ),
        migrations.AddField(
            model_name='test',
            name='userlogin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inrtracker.User'),
        ),
        migrations.AddField(
            model_name='takendrugs',
            name='userlogin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inrtracker.User'),
        ),
        migrations.AddField(
            model_name='inr',
            name='userlogin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inrtracker.User'),
        ),
    ]
