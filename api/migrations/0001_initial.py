# Generated by Django 3.0.5 on 2021-03-08 09:29

import jsonfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Websites',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_website', models.CharField(default='', max_length=250)),
                ('websites', models.CharField(default='', max_length=250)),
                ('list_website', jsonfield.fields.JSONField(null=True)),
            ],
        ),
    ]
