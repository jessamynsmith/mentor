# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import enumfields.fields
import codementor.models


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0012_auto_20151027_0135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='continent',
            field=enumfields.fields.EnumField(default=b'Unknown', max_length=20, enum=codementor.models.Continent),
        ),
        migrations.AlterField(
            model_name='client',
            name='gender',
            field=enumfields.fields.EnumField(default=b'Unknown', max_length=20, enum=codementor.models.Gender),
        ),
    ]
