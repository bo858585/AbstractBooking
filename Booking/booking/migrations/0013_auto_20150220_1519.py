# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0012_auto_20150219_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='cash',
            field=models.DecimalField(
                default=Decimal('0.0'), max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
    ]
