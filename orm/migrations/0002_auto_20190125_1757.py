# Generated by Django 2.2a1 on 2019-01-25 17:57

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('orm', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gaugeboson',
            name='deletion_date',
            field=models.DateTimeField(default=datetime.datetime(2029, 1, 24, 17, 57, 41, 994477, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='lepton',
            name='deletion_date',
            field=models.DateTimeField(default=datetime.datetime(2029, 1, 24, 17, 57, 41, 994477, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='quark',
            name='deletion_date',
            field=models.DateTimeField(default=datetime.datetime(2029, 1, 24, 17, 57, 41, 994477, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='scalarboson',
            name='deletion_date',
            field=models.DateTimeField(default=datetime.datetime(2029, 1, 24, 17, 57, 41, 994477, tzinfo=utc)),
        ),
    ]
