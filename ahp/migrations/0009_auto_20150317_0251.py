# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahp', '0008_level_levelnodes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='edge',
            name='node',
        ),
        migrations.RemoveField(
            model_name='edge',
            name='parent_id',
        ),
        migrations.AddField(
            model_name='edge',
            name='parent',
            field=models.ForeignKey(related_name='children', blank=True, to='ahp.Edge', null=True),
            preserve_default=True,
        ),
    ]
