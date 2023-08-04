from django.shortcuts import render, HttpResponse


from django.shortcuts import render, redirect
from .models import SessionRequest, Etudiant
from .user_management import *
import random
import string
import os

import threading

from django.conf import settings
from django.core.mail import send_mail

def index(request):

    return render(request, 'app/index.html')


def session_request(request):
    if request.method == 'POST':
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        specialite = request.POST['specialité']
        email = request.POST['email']
        telephone = request.POST['telephone']
        intitule_pfe = request.POST['intitule']
        encadrant = request.POST['encadrant']
        date_fin_pfe = request.POST['date_fin']

        etudiant = Etudiant(
            nom=nom,
            prenom=prenom,
            specialite=specialite,
            email=email,
            telephone=telephone,
            intitule_pfe=intitule_pfe,
            encadrant=encadrant,
            date_fin_pfe=date_fin_pfe,
        )
        etudiant.save()
        #check if etudiant existed already in the database
        if Etudiant.objects.filter(email=email).exists():
            etudiant = Etudiant.objects.get(email=email)
            return redirect('erreur', message='Vous avez déjà fait une demande auparavant ! Veuillez revenir à la page d\'accueil et cliquer sur "Redemander une session"')
        print('etudiant crée !')

        subject = "Demande de session en cours de traitement"
        body = f"Bonjour {nom} {prenom},\n\nNous avons bien reçu votre demande de session GPU. Votre demande est actuellement en cours de traitement. Nous vous informerons dès que votre session sera prête.\n\nCordialement,\nService Réseaux ESI"
        send_email(email, subject, body)
        session_choice = request.POST['session_choice']
                # Generate a random secure password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        date_debut, date_fin = get_schedule(session_choice)
        session_request = SessionRequest(
            etudiant=etudiant,
            type='Nouvelle',
            password=password,
            session_choice=session_choice,
            date_debut=date_debut,
            date_fin=date_fin,
        )
        session_request.save()
        print('session created !')
        subject = "Informations de connexion à votre session GPU"
        body = f"Bonjour {nom} {prenom},\n\nNous vous informons que votre session GPU sera disponible à partir du {date_debut} jusqu'au {date_fin}.\n\nVoici les informations de connexion à votre session :\n\nAdresse IP de la machine: 10.0.0.24\nNom d'utilisateur : {email}\nMot de passe : {password}\n\nCordialement,\nService Réseaux ESI"
        send_email(email, subject, body)

        
        # send an email in a thread to the student before 30 min of the date_debut of the session
        thread = threading.Thread(target=send_email_delayed, args=(email, subject, body,timedelta(minutes=30),date_debut)).start()
        thread = threading.Thread(target=start_session, args=(etudiant.id, session_request.id ))
        session_request.save()
        print('session processed !')

        # Redirect to a success page after saving the data
        return redirect('success_session_request', id=session_request.id)

    return render(request, 'app/session_request.html')

def session_redemand(request):
    if request.method == 'POST':
        email = request.POST['email']
        session_choice = request.POST['session_choice']
        etudiant = Etudiant.objects.get(email=email)
        date_debut, date_fin = get_schedule(session_choice)
        session_request = SessionRequest.create(etudiant,
                                                session_choice=session_choice,
                                                type='Redemande',
                                                password=etudiant.password,
                                                date_debut=date_debut,
                                                date_fin=date_fin,
                                                )
        session_request.save()
        print('session created !')

        subject = "Informations de connexion à votre session GPU"
        body = f"Bonjour {etudiant.nom} {etudiant.prenom},\n\nNous vous informons que votre session GPU sera disponible à partir du {date_debut} jusqu'au {date_fin}.\n\nVoici les informations de connexion à votre session :\n\nAdresse IP de la machine: 10.0.0.24 \nNom d'utilisateur : {email}\nMot de passe : {etudiant.password}\n\nCordialement,\nService Réseaux ESI"
        send_email(email, subject, body)
        # send an email in a thread to the student before 30 min of the date_debut of the session
        thread = threading.Thread(target=send_email_delayed, args=(email, subject, body,timedelta(minutes=30),date_debut)).start()

        thread = threading.Thread(target=start_session, args=(etudiant.id, session_request.id ))
        print('session processed  !')
        # Redirect to a success page after saving the data
        return redirect('success_session_request', id=session_request.id)
    
        
    return render(request, 'app/session_redemand.html')

def success_session_request(request,id):
    session_request = SessionRequest.objects.get(pk=id)
    etudiant = session_request.etudiant
    return render(request, 'app/success.html', {'session_request': session_request,'etudiant':etudiant})

def erreur(request):
    return render(request, 'app/erreur.html')

