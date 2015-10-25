# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import enumfields.fields
import codementor.models


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0005_auto_20151024_0318'),
    ]

    operations = [
        migrations.CreateModel(
            name='PopulationGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', enumfields.fields.EnumField(max_length=20, enum=codementor.models.PopulationGroupType)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='client',
            name='population_groups',
            field=models.ManyToManyField(default=None, to='codementor.PopulationGroup', blank=True),
        ),
    ]
