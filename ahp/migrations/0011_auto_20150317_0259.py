# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahp', '0010_auto_20150317_0255'),
    ]

    operations = [
        migrations.AddField(
            model_name='edge',
            name='node',
            field=models.ForeignKey(related_name='children', blank=True, to='ahp.Node', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='edge',
            name='parent',
            field=models.ForeignKey(related_name='parent', blank=True, to='ahp.Node', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='edge',
            name='project',
            field=models.ForeignKey(to='ahp.Project'),
            preserve_default=True,
        ),
    ]
