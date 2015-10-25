# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0007_race_to_population_group_20151025_1258'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='races',
        ),
        migrations.DeleteModel(
            name='Race',
        ),
    ]
