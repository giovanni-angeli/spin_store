# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-14 09:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Pipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='gaugeboson',
            name='json_field',
            field=models.CharField(default='{}', max_length=10000),
        ),
        migrations.AddField(
            model_name='lepton',
            name='json_field',
            field=models.CharField(default='{}', max_length=10000),
        ),
        migrations.AddField(
            model_name='quark',
            name='json_field',
            field=models.CharField(default='{}', max_length=10000),
        ),
        migrations.AddField(
            model_name='scalarboson',
            name='json_field',
            field=models.CharField(default='{}', max_length=10000),
        ),
    ]
