# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0011_auto_20150219_1916'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='booking',
            options={'default_permissions': (), 'permissions': (
                ('perform_perm', 'Ability to perform created booking'),)},
        ),
    ]
