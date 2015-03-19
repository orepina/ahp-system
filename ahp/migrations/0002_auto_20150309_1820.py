# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='info',
            field=models.CharField(default='groupname', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='node',
            name='name_node',
            field=models.CharField(default='nodename', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='info',
            field=models.CharField(default='username', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='weight',
            name='weight',
            field=models.CharField(default='weight name', max_length=30),
            preserve_default=False,
        ),
    ]
