# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0016_auto_20160919_2016'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeeklyRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('week_end', models.DateField(unique=True)),
                ('unique_clients', models.IntegerField()),
                ('avg_rating', models.DecimalField(max_digits=4, decimal_places=2)),
                ('platform_fee', models.CharField(max_length=5)),
            ],
            options={
                'ordering': ['-week_end'],
            },
        ),
    ]
