# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-23 17:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='offre',
            name='remarques',
            field=models.TextField(blank=True),
        ),
    ]