# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-16 13:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orm', '0005_auto_20180216_1144'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gaugeboson',
            old_name='particle_name',
            new_name='ui_name',
        ),
        migrations.RenameField(
            model_name='lepton',
            old_name='particle_name',
            new_name='ui_name',
        ),
        migrations.RenameField(
            model_name='quark',
            old_name='particle_name',
            new_name='ui_name',
        ),
        migrations.RenameField(
            model_name='scalarboson',
            old_name='particle_name',
            new_name='ui_name',
        ),
    ]
