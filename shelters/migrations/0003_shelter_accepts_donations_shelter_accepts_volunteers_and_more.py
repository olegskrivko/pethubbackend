# Generated by Django 5.2.1 on 2025-06-10 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shelters', '0002_animaltype_shelter_animal_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='shelter',
            name='accepts_donations',
            field=models.BooleanField(default=False, verbose_name='Pieņem ziedojumus'),
        ),
        migrations.AddField(
            model_name='shelter',
            name='accepts_volunteers',
            field=models.BooleanField(default=False, verbose_name='Pieņem brīvprātīgos'),
        ),
        migrations.AddField(
            model_name='shelter',
            name='category',
            field=models.IntegerField(blank=True, choices=[(1, 'Municipal Shelter'), (2, 'Animal Rescue'), (3, 'Sanctuary'), (4, 'Private Shelter'), (5, 'Other')], null=True, verbose_name='Kategorija'),
        ),
        migrations.AddField(
            model_name='shelter',
            name='is_public',
            field=models.BooleanField(default=True, verbose_name='Atvērts sabiedrībai'),
        ),
        migrations.AddField(
            model_name='shelter',
            name='offers_adoption',
            field=models.BooleanField(default=False, verbose_name='Piedāvā adopciju'),
        ),
        migrations.AddField(
            model_name='shelter',
            name='size',
            field=models.IntegerField(blank=True, choices=[(1, 'Small (1-20 animals)'), (2, 'Medium (21-100 animals)'), (3, 'Large (100+ animals)')], null=True, verbose_name='Izmērs'),
        ),
    ]
