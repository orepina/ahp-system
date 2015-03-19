# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahp', '0004_user_id_hash'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('info', models.CharField(default=b'', max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='group',
            name='project',
            field=models.ForeignKey(default='1', to='ahp.Project'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='node',
            name='project',
            field=models.ForeignKey(default='1', to='ahp.Project'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='project',
            field=models.ForeignKey(default='1', to='ahp.Project'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='weight',
            name='project',
            field=models.ForeignKey(default='1', to='ahp.Project'),
            preserve_default=False,
        ),
    ]
