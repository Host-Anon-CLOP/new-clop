# Generated by Django 4.1.7 on 2023-04-02 13:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('nations', '0007_alter_nation_options'),
        ('markets', '0002_order_created_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['created_at']},
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_id', models.PositiveIntegerField()),
                ('amount', models.PositiveIntegerField()),
                ('price', models.PositiveIntegerField()),
                ('order_type', models.PositiveSmallIntegerField(choices=[(1, 'Buy'), (2, 'Sell')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions_as_buyer', to='nations.nation')),
                ('item_type', models.ForeignKey(limit_choices_to={'model__in': ('resource',)}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions_as_seller', to='nations.nation')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]
