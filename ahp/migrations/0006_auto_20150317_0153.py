# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahp', '0005_auto_20150313_1706'),
    ]

    operations = [
        migrations.CreateModel(
            name='Edge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parent_id', models.CharField(default=b'', max_length=30)),
                ('node', models.ForeignKey(to='ahp.Node')),
                ('project', models.ForeignKey(to='ahp.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupNode',
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
        migrations.CreateModel(
            name='UsersNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('node', models.ForeignKey(to='ahp.Node')),
                ('user', models.ForeignKey(to='ahp.User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameField(
            model_name='node',
            old_name='node_id',
            new_name='info',
        ),
        migrations.RemoveField(
            model_name='node',
            name='level',
        ),
        migrations.RemoveField(
            model_name='node',
            name='parent_id',
        ),
        migrations.AlterField(
            model_name='weight',
            name='node',
            field=models.ForeignKey(to='ahp.Edge'),
            preserve_default=True,
        ),
    ]
