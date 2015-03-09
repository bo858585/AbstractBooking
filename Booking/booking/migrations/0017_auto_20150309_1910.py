# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0016_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='booking',
            options={'permissions': (('perform_perm', 'Ability to perform created booking'),)},
        ),
    ]
