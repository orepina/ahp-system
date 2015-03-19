# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahp', '0002_auto_20150309_1820'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='node',
            name='name_node',
        ),
        migrations.RemoveField(
            model_name='node',
            name='parent',
        ),
        migrations.AddField(
            model_name='node',
            name='level',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='node_id',
            field=models.CharField(default=b'', max_length=30),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='parent_id',
            field=models.CharField(default=b'', max_length=30),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.CharField(default=b'', max_length=30),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='info',
            field=models.CharField(default=b'', max_length=30),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='info',
            field=models.CharField(default=b'', max_length=30),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weight',
            name='weight',
            field=models.CharField(default=b'', max_length=30),
            preserve_default=True,
        ),
    ]
