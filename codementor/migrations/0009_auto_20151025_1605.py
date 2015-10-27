# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import enumfields.fields
import codementor.models


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0008_auto_20151025_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='continent2',
            field=enumfields.fields.EnumField(blank=True, max_length=20, null=True, enum=codementor.models.Continent),
        ),
        migrations.AddField(
            model_name='client',
            name='gender2',
            field=enumfields.fields.EnumField(blank=True, max_length=20, null=True, enum=codementor.models.Gender),
        ),
        migrations.AddField(
            model_name='payment',
            name='type2',
            field=enumfields.fields.EnumField(default=b'Session', max_length=30, enum=codementor.models.PaymentType2),
        ),
        migrations.AddField(
            model_name='payout',
            name='method2',
            field=enumfields.fields.EnumField(default=b'PayPal', max_length=10, enum=codementor.models.PayoutMethod2),
        ),
    ]
