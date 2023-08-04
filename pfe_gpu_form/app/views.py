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


        # Start a new thread to delete the user after the session expires
        thread = threading.Thread(target=manage_user, args=(etudiant.email, password, session_request.session_choice )).start()
        
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

        # Start a new thread to delete the user after the session expires

        thread = threading.Thread(target=redemand_session, args=(etudiant.email, etudiant.password, session_request.session_choice )).start()
        print('session processed  !')
        # Redirect to a success page after saving the data
        return redirect('success_session_request', id=session_request.id)
    
        
    return render(request, 'app/session_redemand.html')

def success_session_request(request,id):
    session_request = SessionRequest.objects.get(pk=id)
    etudiant = session_request.etudiant
    return render(request, 'app/success.html', {'session_request': session_request,'etudiant':etudiant})



