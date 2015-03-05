# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0014_auto_20150220_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(default=b'pending', max_length=30, choices=[(b'pending', '\u041e\u0436\u0438\u0434\u0430\u0435\u0442 \u0438\u0441\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044f'), (b'waiting_for_approval', '\u041e\u0436\u0438\u0434\u0430\u0435\u0442 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u044f \u0437\u0430\u043a\u0430\u0437\u0447\u0438\u043a\u043e\u043c'), (b'running', '\u0412\u0437\u044f\u0442 \u043d\u0430 \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435'), (b'completed', '\u0417\u0430\u0432\u0435\u0440\u0448\u0435\u043d')]),
            preserve_default=True,
        ),
    ]
