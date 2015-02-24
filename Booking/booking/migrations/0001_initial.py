# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('text', models.TextField(max_length=200)),
                ('price', models.IntegerField(default=100)),
                ('status', models.CharField(default=b'pending', max_length=30, choices=[(b'pending', '\u041e\u0436\u0438\u0434\u0430\u0435\u0442 \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f'), (
                    b'running', '\u0412\u0437\u044f\u0442 \u043d\u0430 \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435'), (b'completed', '\u0417\u0430\u0432\u0435\u0440\u0448\u0435\u043d')])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(
                    related_name='customer_booking', to=settings.AUTH_USER_MODEL)),
                ('performer', models.ForeignKey(
                    related_name='performer_booking', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
