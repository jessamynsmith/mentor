# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0004_auto_20151014_1932'),
    ]

    operations = [
        migrations.CreateModel(
            name='Race',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.IntegerField(default=5)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('started_at', models.DateTimeField()),
                ('length', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ['-started_at'],
            },
        ),
        migrations.RemoveField(
            model_name='payment',
            name='length',
        ),
        migrations.AddField(
            model_name='client',
            name='continent',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='client',
            name='gender',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='client',
            name='started_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='session',
            name='client',
            field=models.ForeignKey(related_name='sessions', to='codementor.Client'),
        ),
        migrations.AddField(
            model_name='session',
            name='review',
            field=models.OneToOneField(null=True, blank=True, to='codementor.Review'),
        ),
        migrations.AddField(
            model_name='client',
            name='races',
            field=models.ManyToManyField(default=None, to='codementor.Race', blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='session',
            field=models.OneToOneField(null=True, blank=True, to='codementor.Session'),
        ),
    ]
