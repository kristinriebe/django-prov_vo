# -*- coding: utf-8 -*-
# Generated by Kristin Riebe, 2017-06-07 8:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prov_vo', '0003_agent_email'),
    ]

    operations = [
        migrations.RenameField(
            'entity', 'status', 'rights',
        ),
    ]