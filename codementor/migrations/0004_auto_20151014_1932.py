# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0003_payout_total_earnings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='payout',
            name='date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='review',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
