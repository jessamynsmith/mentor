# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0013_auto_20151027_0145'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='username',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
