# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0002_auto_20150929_0426'),
    ]

    operations = [
        migrations.AddField(
            model_name='payout',
            name='total_earnings',
            field=models.DecimalField(default=Decimal('0'), max_digits=10, decimal_places=2),
        ),
    ]
