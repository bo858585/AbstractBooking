# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='price',
            field=models.DecimalField(default=100, max_digits=6, decimal_places=0),
            preserve_default=True,
        ),
    ]
