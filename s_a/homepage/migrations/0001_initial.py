# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-27 05:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=100)),
                ('confidence', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='KeyPhrase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=100)),
                ('confidence', models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('confidence', models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sentiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('confidence', models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transcription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=1000)),
                ('entities', models.ManyToManyField(blank=True, null=True, to='homepage.Entity')),
                ('key_phrases', models.ManyToManyField(blank=True, null=True, to='homepage.KeyPhrase')),
                ('language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='homepage.Language')),
                ('sentiment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='homepage.Sentiment')),
            ],
        ),
    ]