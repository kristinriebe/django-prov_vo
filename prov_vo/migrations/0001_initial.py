# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-05 10:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, null=True)),
                ('type', models.CharField(choices=[('obs:Observation', 'obs:Observation'), ('obs:Reduction', 'obs:Reduction'), ('obs:Classification', 'obs:Classification'), ('obs:Crossmatch', 'obs:Crossmatch'), ('calc:ChemicalPipeline', 'calc:ChemicalPipeline'), ('calc:Distances', 'calc:Distances'), ('other', 'other')], max_length=128, null=True)),
                ('annotation', models.CharField(blank=True, max_length=1024, null=True)),
                ('startTime', models.DateTimeField(null=True)),
                ('endTime', models.DateTimeField(null=True)),
                ('doculink', models.CharField(blank=True, max_length=512, null=True, verbose_name='documentation link')),
            ],
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, null=True)),
                ('type', models.CharField(choices=[('voprov:Organization', 'voprov:Organization'), ('voprov:Individual', 'voprov:Individual')], max_length=128, null=True)),
                ('email', models.CharField(blank=True, max_length=128, null=True)),
                ('address', models.CharField(blank=True, max_length=128, null=True)),
                ('annotation', models.CharField(blank=True, max_length=1024, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, null=True)),
                ('type', models.CharField(choices=[('voprov:Collection', 'voprov:Collection'), ('voprov:Entity', 'voprov:Entity')], max_length=128, null=True)),
                ('annotation', models.CharField(blank=True, max_length=1024, null=True)),
                ('rights', models.CharField(blank=True, choices=[('voprov:public', 'voprov:public'), ('voprov:restricted', 'voprov:restricted'), ('voprov:internal', 'voprov:internal')], max_length=128, null=True)),
                ('dataType', models.CharField(blank=True, max_length=128, null=True)),
                ('storageLocation', models.CharField(blank=True, max_length=1024, null=True, verbose_name='storage location')),
            ],
        ),
        migrations.CreateModel(
            name='HadMember',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='HadStep',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Used',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('time', models.DateTimeField(null=True)),
                ('role', models.CharField(blank=True, max_length=128, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WasAssociatedWith',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('role', models.CharField(blank=True, max_length=128, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WasAttributedTo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('role', models.CharField(blank=True, max_length=128, null=True)),
                ('agent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prov_vo.Agent')),
            ],
        ),
        migrations.CreateModel(
            name='WasDerivedFrom',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='WasGeneratedBy',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('time', models.DateTimeField(null=True)),
                ('role', models.CharField(blank=True, max_length=128, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WasInformedBy',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='ActivityFlow',
            fields=[
                ('activity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='prov_vo.Activity')),
            ],
            bases=('prov_vo.activity',),
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('entity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='prov_vo.Entity')),
            ],
            bases=('prov_vo.entity',),
        ),
        migrations.AddField(
            model_name='wasinformedby',
            name='informant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='informed', to='prov_vo.Activity'),
        ),
        migrations.AddField(
            model_name='wasinformedby',
            name='informed',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prov_vo.Activity'),
        ),
        migrations.AddField(
            model_name='wasgeneratedby',
            name='activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prov_vo.Activity'),
        ),
        migrations.AddField(
            model_name='wasgeneratedby',
            name='entity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prov_vo.Entity'),
        ),
        migrations.AddField(
            model_name='wasderivedfrom',
            name='generatedEntity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prov_vo.Entity'),
        ),
        migrations.AddField(
            model_name='wasderivedfrom',
            name='usedEntity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='generatedEntity', to='prov_vo.Entity'),
        ),
        migrations.AddField(
            model_name='wasattributedto',
            name='entity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prov_vo.Entity'),
        ),
        migrations.AddField(
            model_name='wasassociatedwith',
            name='activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prov_vo.Activity'),
        ),
        migrations.AddField(
            model_name='wasassociatedwith',
            name='agent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prov_vo.Agent'),
        ),
        migrations.AddField(
            model_name='used',
            name='activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prov_vo.Activity'),
        ),
        migrations.AddField(
            model_name='used',
            name='entity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prov_vo.Entity'),
        ),
        migrations.AddField(
            model_name='hadstep',
            name='activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activityFlow', to='prov_vo.Activity'),
        ),
        migrations.AddField(
            model_name='hadmember',
            name='entity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ecollection', to='prov_vo.Entity'),
        ),
        migrations.AddField(
            model_name='hadstep',
            name='activityFlow',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prov_vo.ActivityFlow'),
        ),
        migrations.AddField(
            model_name='hadmember',
            name='collection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='prov_vo.Collection'),
        ),
    ]
