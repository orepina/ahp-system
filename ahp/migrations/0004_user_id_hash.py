# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahp', '0003_auto_20150309_2312'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='id_hash',
            field=models.CharField(default=b'', max_length=15),
            preserve_default=True,
        ),
    ]
