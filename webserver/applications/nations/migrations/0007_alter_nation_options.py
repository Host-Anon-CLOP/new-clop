# Generated by Django 4.1.7 on 2023-04-01 17:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nations', '0006_nationbuilding_nationresource'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='nation',
            options={'ordering': ['created_on']},
        ),
    ]
