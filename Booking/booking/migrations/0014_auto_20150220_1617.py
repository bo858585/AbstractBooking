# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0013_auto_20150220_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='text',
            field=models.TextField(max_length=4000),
            preserve_default=True,
        ),
    ]
