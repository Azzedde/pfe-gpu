# Generated by Django 4.2.3 on 2023-08-04 04:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Etudiant',
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
                ('password', models.CharField(blank=True, max_length=100)),
                ('nb_infractions', models.IntegerField(default=0)),
                ('is_banned', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SessionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_demande', models.DateTimeField(auto_now_add=True)),
                ('date_debut', models.DateTimeField(blank=True, null=True)),
                ('date_fin', models.DateTimeField(blank=True, null=True)),
                ('password', models.CharField(blank=True, max_length=100)),
                ('type', models.CharField(choices=[('Nouvelle', 'Nouvelle'), ('Redemande', 'Redemande')], default='Nouvelle', max_length=10)),
                ('session_choice', models.CharField(choices=[('Matinale', '7:00 - 14:00'), ('Après-midi', '14:30 - 23:59')], max_length=10)),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.etudiant')),
            ],
        ),
    ]
