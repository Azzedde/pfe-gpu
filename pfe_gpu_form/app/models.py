from django.db import models

# Create your models here.


from django.db import models

class SessionRequest(models.Model):
    SPECIALITY_CHOICES = (
        ('SIQ', 'SIQ'),
        ('SID', 'SID'),
        ('SIL', 'SIL'),
        ('SIT', 'SIT'),
    )

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    specialite = models.CharField(max_length=3, choices=SPECIALITY_CHOICES)
    email = models.EmailField()
    telephone = models.CharField(max_length=15)
    intitule_pfe = models.TextField()
    encadrant = models.CharField(max_length=100)
    date_fin_pfe = models.DateField()
    password = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"
