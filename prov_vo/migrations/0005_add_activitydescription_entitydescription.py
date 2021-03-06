# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-27 14:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prov_vo', '0004_parameter_activity_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityDescription',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, null=True)),
                ('type', models.CharField(choices=[('obs:Observation', 'obs:Observation'), ('obs:Reduction', 'obs:Reduction'), ('obs:Classification', 'obs:Classification'), ('obs:Crossmatch', 'obs:Crossmatch'), ('calc:ChemicalPipeline', 'calc:ChemicalPipeline'), ('calc:Distances', 'calc:Distances'), ('other', 'other')], max_length=128, null=True)),
                ('subtype', models.CharField(blank=True, max_length=128, null=True)),
                ('annotation', models.CharField(blank=True, max_length=1024, null=True)),
                ('doculink', models.CharField(blank=True, max_length=512, null=True, verbose_name='documentation link')),
                ('code', models.CharField(blank=True, max_length=128, null=True)),
                ('version', models.CharField(blank=True, max_length=128, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EntityDescription',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, null=True)),
                ('annotation', models.CharField(blank=True, max_length=1024, null=True)),
                ('category', models.CharField(blank=True, max_length=128, null=True)),
                ('doculink', models.CharField(blank=True, max_length=512, null=True, verbose_name='documentation link')),
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='description',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prov_vo.ActivityDescription'),
        ),
        migrations.AddField(
            model_name='entity',
            name='description',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prov_vo.EntityDescription'),
        ),
    ]
