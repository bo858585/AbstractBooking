# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_auto_20150212_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='price',
            field=models.DecimalField(default=100, max_digits=8, decimal_places=2),
            preserve_default=True,
        ),
    ]
