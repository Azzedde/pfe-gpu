# Generated by Django 4.2.3 on 2023-07-29 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SessionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('specialite', models.CharField(choices=[('SIQ', 'SIQ'), ('SID', 'SID'), ('SIL', 'SIL'), ('SIT', 'SIT')], max_length=3)),
                ('email', models.EmailField(max_length=254)),
                ('telephone', models.CharField(max_length=15)),
                ('intitule_pfe', models.TextField()),
                ('encadrant', models.CharField(max_length=100)),
                ('date_fin_pfe', models.DateField()),
            ],
        ),
    ]
