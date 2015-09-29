# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(default=0)),
                ('date', models.DateField()),
                ('length', models.IntegerField(null=True, blank=True)),
                ('free_preview', models.BooleanField(default=False)),
                ('earnings', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Payout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('method', models.IntegerField(default=0)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.AlterModelOptions(
            name='client',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['-date']},
        ),
        migrations.AlterField(
            model_name='review',
            name='reviewer',
            field=models.ForeignKey(related_name='reviews', to='codementor.Client'),
        ),
        migrations.AddField(
            model_name='payment',
            name='client',
            field=models.ForeignKey(related_name='payments', to='codementor.Client'),
        ),
        migrations.AddField(
            model_name='payment',
            name='payout',
            field=models.ForeignKey(related_name='payments', blank=True, to='codementor.Payout', null=True),
        ),
    ]
