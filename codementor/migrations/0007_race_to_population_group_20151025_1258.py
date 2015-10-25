# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_population_group(apps, schema_editor):
    from codementor.models import PopulationGroupType
    PopulationGroup = apps.get_model("codementor", "PopulationGroup")

    population_groups = {}
    for item in PopulationGroupType:
        population_group, created = PopulationGroup.objects.get_or_create(name=item)
        population_groups[population_group.name.value] = population_group

    Client = apps.get_model("codementor", "Client")
    for client in Client.objects.all():
        for race in client.races.all():
            if race:
                if race.name in (0, 1):
                    # (AMERICAN_NATIVE , AUSTRALIAN_NATIVE) => INDIGENOUS
                    client.population_groups.add(population_groups['Indigenous'])
                elif race.name == 2:
                    # BLACK => BLACK
                    client.population_groups.add(population_groups['Black'])
                elif race.name == 3:
                    # EAST_ASIAN => CHINESE
                    client.population_groups.add(population_groups['Chinese'])
                elif race.name == 4:
                    # SOUTH_ASIAN => SOUTH_ASIAN
                    client.population_groups.add(population_groups['South Asian'])
                elif race.name == 5:
                    # WHITE => WHITE
                    client.population_groups.add(population_groups['White'])
                elif race.name == 6:
                    # MIDDLE_EASTERN => ARAB
                    client.population_groups.add(population_groups['Arab'])
                elif race.name == 7:
                    # LATINO => LATIN_AMERICAN
                    client.population_groups.add(population_groups['Latin American'])
        client.save()


def set_race(apps, schema_editor):
    from codementor.models import RaceType
    Race = apps.get_model("codementor", "Race")

    races = {}
    for item in RaceType.items():
        race, created = Race.objects.get_or_create(name=item[1])
        races[race.name] = race

    Client = apps.get_model("codementor", "Client")
    for client in Client.objects.all():
        for population_group in client.population_groups.all():
            if population_group:
                if population_group.name.value == 'Indigenous':
                    # INDIGENOUS => AMERICAN_NATIVE
                    client.races.add(races[0])
                elif population_group.name.value == 'Black':
                    # BLACK => BLACK
                    client.races.add(races[2])
                elif population_group.name.value in ('Chinese', 'Filipino', 'Southeast Asian',
                                                     'Korean', 'Japanese'):
                    # (CHINESE, FILIPINO, SOUTHEAST_ASIAN, KOREAN, JAPANESE) => EAST_ASIAN
                    client.races.add(races[3])
                elif population_group.name.value == 'South Asian':
                    # SOUTH_ASIAN => SOUTH_ASIAN
                    client.races.add(races[4])
                elif population_group.name.value == 'White':
                    # WHITE => WHITE
                    client.races.add(races[5])
                elif population_group.name in ('Arab', 'West Asian'):
                    # (ARAB, WEST_ASIAN) => MIDDLE_EASTERN
                    client.races.add(races[6])
                elif population_group.name == 'Latin American':
                    # LATIN_AMERICAN => LATINO
                    client.races.add(races[7])
        client.save()


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0006_auto_20151025_1444'),
    ]

    operations = [
        migrations.RunPython(set_population_group, set_race),
    ]
