# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import enumfields.fields
import codementor.models


def set_empty_to_null(apps, schema_editor):
    Client = apps.get_model("codementor", "Client")
    for client in Client.objects.all():
        if client.continent == codementor.models.Continent.UNKNOWN:
            client.continent = None
        if client.gender == codementor.models.Gender.UNKNOWN:
            client.gender = None
        client.save()


def set_null_to_empty(apps, schema_editor):
    Client = apps.get_model("codementor", "Client")
    for client in Client.objects.all():
        if client.continent is None:
            client.continent = codementor.models.Continent.UNKNOWN
        if client.gender is None:
            client.gender = codementor.models.Gender.UNKNOWN
        client.save()


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0015_session_session_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='continent',
            field=enumfields.fields.EnumField(blank=True, max_length=20, null=True, enum=codementor.models.Continent),
        ),
        migrations.AlterField(
            model_name='client',
            name='gender',
            field=enumfields.fields.EnumField(blank=True, max_length=20, null=True, enum=codementor.models.Gender),
        ),
        migrations.RunPython(set_empty_to_null, set_null_to_empty),
    ]
