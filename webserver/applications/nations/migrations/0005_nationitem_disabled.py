# Generated by Django 4.1.7 on 2023-03-05 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nations', '0004_alter_nation_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='nationitem',
            name='disabled',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
