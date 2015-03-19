# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahp', '0007_auto_20150317_0158'),
    ]

    operations = [
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('info', models.CharField(default=b'', max_length=30)),
                ('project', models.ForeignKey(to='ahp.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LevelNodes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.ForeignKey(to='ahp.Level')),
                ('node', models.ForeignKey(to='ahp.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
