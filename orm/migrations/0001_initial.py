# Generated by Django 2.2a1 on 2019-01-25 17:57

import datetime
from django.db import migrations, models
import django.utils.timezone
from django.utils.timezone import utc
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='GaugeBoson',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='UUID')),
                ('ui_name', models.CharField(max_length=200, verbose_name='name')),
                ('tenant_id', models.UUIDField(blank=True, editable=False, null=True, verbose_name="tenant's uuid")),
                ('_parameters', models.TextField(blank=True, db_column='parameters', default='{}', verbose_name='parameters')),
                ('parameters_schema_name', models.CharField(default='Generic', max_length=200, verbose_name='jsonschema name')),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('deletion_date', models.DateTimeField(default=datetime.datetime(2029, 1, 24, 17, 57, 19, 996586, tzinfo=utc))),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Lepton',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='UUID')),
                ('ui_name', models.CharField(max_length=200, verbose_name='name')),
                ('tenant_id', models.UUIDField(blank=True, editable=False, null=True, verbose_name="tenant's uuid")),
                ('_parameters', models.TextField(blank=True, db_column='parameters', default='{}', verbose_name='parameters')),
                ('parameters_schema_name', models.CharField(default='Generic', max_length=200, verbose_name='jsonschema name')),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('deletion_date', models.DateTimeField(default=datetime.datetime(2029, 1, 24, 17, 57, 19, 996586, tzinfo=utc))),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Pipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Quark',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='UUID')),
                ('ui_name', models.CharField(max_length=200, verbose_name='name')),
                ('tenant_id', models.UUIDField(blank=True, editable=False, null=True, verbose_name="tenant's uuid")),
                ('_parameters', models.TextField(blank=True, db_column='parameters', default='{}', verbose_name='parameters')),
                ('parameters_schema_name', models.CharField(default='Generic', max_length=200, verbose_name='jsonschema name')),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('deletion_date', models.DateTimeField(default=datetime.datetime(2029, 1, 24, 17, 57, 19, 996586, tzinfo=utc))),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ScalarBoson',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='UUID')),
                ('ui_name', models.CharField(max_length=200, verbose_name='name')),
                ('tenant_id', models.UUIDField(blank=True, editable=False, null=True, verbose_name="tenant's uuid")),
                ('_parameters', models.TextField(blank=True, db_column='parameters', default='{}', verbose_name='parameters')),
                ('parameters_schema_name', models.CharField(default='Generic', max_length=200, verbose_name='jsonschema name')),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('deletion_date', models.DateTimeField(default=datetime.datetime(2029, 1, 24, 17, 57, 19, 996586, tzinfo=utc))),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
