# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahp', '0006_auto_20150317_0153'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupNodes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default=b'', max_length=30)),
                ('count', models.IntegerField()),
                ('group', models.ForeignKey(to='ahp.Group')),
                ('node', models.ForeignKey(to='ahp.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameModel(
            old_name='UsersNode',
            new_name='UserNodes',
        ),
        migrations.RemoveField(
            model_name='groupnode',
            name='group',
        ),
        migrations.RemoveField(
            model_name='groupnode',
            name='node',
        ),
        migrations.DeleteModel(
            name='GroupNode',
        ),
    ]
