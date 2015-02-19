# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0008_systemaccount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemaccount',
            name='commission',
            field=models.DecimalField(default=Decimal('0.03'), max_digits=3, decimal_places=2),
            preserve_default=True,
        ),
    ]
