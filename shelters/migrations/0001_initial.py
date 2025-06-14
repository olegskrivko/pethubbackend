# Generated by Django 5.2.1 on 2025-06-05 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SocialMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.IntegerField(choices=[(1, 'Facebook'), (2, 'Instagram'), (3, 'X'), (4, 'LinkedIn'), (5, 'YouTube'), (6, 'TikTok'), (7, 'Pinterest'), (8, 'Snapchat')], verbose_name='Platforma')),
                ('profile_url', models.URLField()),
                ('is_official', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Shelter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nosaukums')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Apraksts')),
                ('website', models.URLField(blank=True, null=True, verbose_name='Vietne')),
                ('country', models.CharField(blank=True, choices=[('LV', 'Latvija'), ('EE', 'Igaunija'), ('LT', 'Lietuva')], max_length=2, null=True, verbose_name='Valsts')),
                ('region', models.CharField(blank=True, max_length=100, null=True, verbose_name='Reģions')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='Pilsēta')),
                ('street', models.CharField(blank=True, max_length=200, null=True, verbose_name='Iela')),
                ('postal_code', models.CharField(blank=True, max_length=20, null=True, verbose_name='Pasta indekss')),
                ('full_address', models.TextField(blank=True, null=True, verbose_name='Adrese')),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Ģeogrāfiskais platums')),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Ģeogrāfiskais garums')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True, verbose_name='Telefona numurs')),
                ('phone_code', models.CharField(blank=True, choices=[('371', 'LV (+371)'), ('370', 'LT (+370)'), ('372', 'EE (+372)')], max_length=4, null=True, verbose_name='Telefona kods')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='E-pasts')),
                ('social_media', models.ManyToManyField(blank=True, related_name='shelters', to='shelters.socialmedia', verbose_name='Sociālie mediji')),
            ],
            options={
                'verbose_name': 'Shelter',
                'verbose_name_plural': 'Shelters',
                'ordering': ['name'],
            },
        ),
    ]
