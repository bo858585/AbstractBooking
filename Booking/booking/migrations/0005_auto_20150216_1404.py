# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_auto_20150213_1336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='text',
            field=models.TextField(max_length=500),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='booking',
            name='title',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
    ]
