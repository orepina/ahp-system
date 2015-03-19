# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahp', '0009_auto_20150317_0251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edge',
            name='project',
            field=models.ForeignKey(to='ahp.Node'),
            preserve_default=True,
        ),
    ]
