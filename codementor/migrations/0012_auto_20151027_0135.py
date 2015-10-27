# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0011_auto_20151027_0058'),
    ]

    operations = [
        migrations.RenameField(
            model_name='client',
            old_name='continent2',
            new_name='continent',
        ),
        migrations.RenameField(
            model_name='client',
            old_name='gender2',
            new_name='gender',
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='type2',
            new_name='type',
        ),
        migrations.RenameField(
            model_name='payout',
            old_name='method2',
            new_name='method',
        ),
    ]
