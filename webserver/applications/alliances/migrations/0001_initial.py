# Generated by Django 4.1.7 on 2023-03-30 08:09

import applications.alliances.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alliance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('flag', models.ImageField(blank=True, null=True, upload_to=applications.alliances.models.flag_upload)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AllianceMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('rank', models.PositiveSmallIntegerField(choices=[(1, 'Leader'), (2, 'Second in Command'), (4, 'General'), (5, 'Officer'), (6, 'Quartermaster'), (10, 'Senior Member'), (100, 'Member')], default=100)),
                ('alliance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='alliances.alliance')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='alliance', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]