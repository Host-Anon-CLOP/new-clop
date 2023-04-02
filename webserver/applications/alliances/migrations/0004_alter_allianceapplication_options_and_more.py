# Generated by Django 4.1.7 on 2023-04-01 17:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alliances', '0003_alter_alliancemember_options_alliance_banner_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='allianceapplication',
            options={'ordering': ['created_on']},
        ),
        migrations.AlterModelOptions(
            name='alliancemember',
            options={'ordering': ['rank', 'joined_on']},
        ),
        migrations.RenameField(
            model_name='alliance',
            old_name='created_at',
            new_name='created_on',
        ),
        migrations.RenameField(
            model_name='allianceapplication',
            old_name='created_at',
            new_name='created_on',
        ),
        migrations.RenameField(
            model_name='alliancemember',
            old_name='joined_at',
            new_name='joined_on',
        ),
    ]