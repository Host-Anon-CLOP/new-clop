# Generated by Django 4.1.7 on 2023-03-05 15:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bundleitem',
            unique_together={('bundle', 'item_type', 'item_id')},
        ),
    ]
