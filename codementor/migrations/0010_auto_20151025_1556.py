# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_continent2(apps, schema_editor):
    from codementor.models import Continent

    Client = apps.get_model("codementor", "Client")
    for item in Client.objects.all():
        if item.continent == 0:
            item.continent2 = Continent.AFRICA
        elif item.continent == 1:
            item.continent2 = Continent.ANTARCTICA
        elif item.continent == 2:
            item.continent2 = Continent.ASIA
        elif item.continent == 3:
            item.continent2 = Continent.AUSTRALIA
        elif item.continent == 4:
            item.continent2 = Continent.EUROPE
        elif item.continent == 5:
            item.continent2 = Continent.NORTH_AMERICA
        elif item.continent == 6:
            item.continent2 = Continent.SOUTH_AMERICA
        item.save()


def set_continent(apps, schema_editor):
    from codementor.models import Continent

    Client = apps.get_model("codementor", "Client")
    for item in Client.objects.all():
        if item.continent2 == Continent.AFRICA:
            item.continent = 0
        elif item.continent2 == Continent.ANTARCTICA:
            item.continent = 1
        elif item.continent2 == Continent.ASIA:
            item.continent = 2
        elif item.continent2 == Continent.AUSTRALIA:
            item.continent = 3
        elif item.continent2 == Continent.EUROPE:
            item.continent = 4
        elif item.continent2 == Continent.NORTH_AMERICA:
            item.continent = 5
        elif item.continent2 == Continent.SOUTH_AMERICA:
            item.continent = 6
        item.save()


def set_gender2(apps, schema_editor):
    from codementor.models import Gender

    Client = apps.get_model("codementor", "Client")
    for item in Client.objects.all():
        if item.gender == 0:
            item.gender2 = Gender.CIS_FEMALE
        elif item.gender == 1:
            item.gender2 = Gender.CIS_MALE
        elif item.gender == 2:
            item.gender2 = Gender.TRANS_FEMALE
        elif item.gender == 3:
            item.gender2 = Gender.TRANS_MALE
        elif item.gender == 4:
            item.gender2 = Gender.AGENDER
        item.save()


def set_gender(apps, schema_editor):
    from codementor.models import Gender

    Client = apps.get_model("codementor", "Client")
    for item in Client.objects.all():
        if item.gender2 == Gender.CIS_FEMALE:
            item.gender = 0
        elif item.gender2 == Gender.CIS_MALE:
            item.gender = 1
        elif item.gender2 == Gender.TRANS_FEMALE:
            item.gender = 2
        elif item.gender2 == Gender.TRANS_MALE:
            item.gender = 3
        elif item.gender2 == Gender.AGENDER:
            item.gender = 4
        item.save()

def set_payout_method2(apps, schema_editor):
    from codementor.models import PayoutMethod

    Payout = apps.get_model("codementor", "Payout")
    for item in Payout.objects.all():
        if item.method == 0:
            item.method2 = PayoutMethod.PAYPAL
        item.save()


def set_payout_method(apps, schema_editor):
    from codementor.models import PayoutMethod

    Payout = apps.get_model("codementor", "Payout")
    for item in Payout.objects.all():
        if item.method2 == PayoutMethod.PAYPAL:
            item.method = 0
        item.save()


def set_payment_type2(apps, schema_editor):
    from codementor.models import PaymentType

    Payment = apps.get_model("codementor", "Payment")
    for item in Payment.objects.all():
        if item.type == 0:
            item.type2 = PaymentType.SESSION
        elif item.type == 1:
            item.type2 = PaymentType.OFFLINE_HELP
        elif item.type == 2:
            item.type2 = PaymentType.MONTHLY
        item.save()


def set_payment_type(apps, schema_editor):
    from codementor.models import PaymentType

    Payment = apps.get_model("codementor", "Payment")
    for item in Payment.objects.all():
        if item.type2 == PaymentType.SESSION:
            item.type = 0
        elif item.type2 == PaymentType.OFFLINE_HELP:
            item.type = 1
        elif item.type2 == PaymentType.MONTHLY:
            item.type = 2
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0009_auto_20151025_1605'),
    ]

    operations = [
        migrations.RunPython(set_continent2, set_continent),
        migrations.RunPython(set_gender2, set_gender),
        migrations.RunPython(set_payout_method2, set_payout_method2),
        migrations.RunPython(set_payment_type2, set_payment_type),
    ]
