# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0009_auto_20150219_1703'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='booking',
            options={'default_permissions': (), 'permissions': (
                ('serve_perm', 'Ability to take and serve created booking'),)},
        ),
    ]
