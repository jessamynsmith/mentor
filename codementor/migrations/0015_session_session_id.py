# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0014_client_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='session_id',
            field=models.CharField(default=1, max_length=12),
            preserve_default=False,
        ),
    ]
