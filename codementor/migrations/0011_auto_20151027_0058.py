# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0010_auto_20151025_1556'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='continent',
        ),
        migrations.RemoveField(
            model_name='client',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='type',
        ),
        migrations.RemoveField(
            model_name='payout',
            name='method',
        ),
    ]
