# Generated by Django 4.1.7 on 2023-03-11 23:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('nations', '0006_nationbuilding_nationresource'),
    ]

    operations = [
        migrations.CreateModel(
            name='NationReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('details', models.TextField(blank=True)),
                ('level', models.PositiveSmallIntegerField(default=25)),
                ('read', models.BooleanField(default=False)),
                ('nation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='nations.nation')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
