# Generated by Django 5.2.1 on 2025-06-13 21:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0003_pet_final_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='petsightinghistory',
            name='event_occurred_at',
        ),
    ]
