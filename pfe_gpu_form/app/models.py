from django.db import models

# Create your models here.


from django.db import models

class SessionRequest(models.Model):
    SessionRequestStatus = (
        ('Nouvelle', 'Nouvelle'),
        ('Redemande', 'Redemande'),
    )
    SESSION_CHOICES = (
        ('Matinale', '7:00 - 14:00'),
        ('Après-midi', '14:30 - 23:59'),
    )
    SESSION_STATUS_CHOICES = (
    ('En attente', 'En attente'),
    ('Active', 'Active'),
    ('Complète', 'Complète'),
)
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='En attente')
    etudiant = models.ForeignKey('Etudiant', on_delete=models.CASCADE)
    date_demande = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateTimeField(null=True,blank=True)
    date_fin = models.DateTimeField(null=True,blank=True)
    password = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=10, choices=SessionRequestStatus, default='Nouvelle')
    session_choice = models.CharField(max_length=10, choices=SESSION_CHOICES)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.etudiant} - {self.session_choice} - {self.date_demande}"

    

class Etudiant(models.Model): 
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
    nb_infractions = models.IntegerField(default=0)
    is_banned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

