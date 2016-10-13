# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-12 15:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('version', models.CharField(max_length=200)),
                ('author', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('more', models.TextField()),
                ('uri', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Input',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('requirement', models.BooleanField(default=False)),
                ('value', models.CharField(max_length=200)),
                ('label', models.CharField(max_length=200)),
                ('max_values', models.IntegerField(default=1)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='japps.Application')),
            ],
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('visibility', models.BooleanField(default=True)),
                ('value', models.CharField(max_length=200)),
                ('label', models.CharField(max_length=200)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='japps.Application')),
            ],
        ),
    ]
