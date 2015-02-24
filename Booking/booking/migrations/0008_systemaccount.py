# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0007_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemAccount',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account', models.DecimalField(
                    default=Decimal('0.00'), max_digits=6, decimal_places=2)),
                ('commission', models.DecimalField(
                    default=Decimal('3.00'), max_digits=5, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
