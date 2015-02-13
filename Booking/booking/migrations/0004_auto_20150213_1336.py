# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_auto_20150212_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='performer',
            field=models.ForeignKey(related_name='performer_booking', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
