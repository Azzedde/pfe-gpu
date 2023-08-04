from django.shortcuts import render, HttpResponse


from django.shortcuts import render, redirect
from .models import SessionRequest
import user_management 
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

        session_request = SessionRequest(
            nom=nom,
            prenom=prenom,
            specialite=specialite,
            email=email,
            telephone=telephone,
            intitule_pfe=intitule_pfe,
            encadrant=encadrant,
            date_fin_pfe=date_fin_pfe,
        )
        session_request.save()
        subject = "Demande de session en cours de traitement"
        body = f"Bonjour {nom} {prenom},\n\nNous avons bien reçu votre demande de session GPU. Votre demande est actuellement en cours de traitement. Nous vous informerons dès que votre session sera prête.\n\nCordialement,\nService Réseaux ESI"
        user_management.send_email(email, subject, body)
        print('session created !')
        # Generate a random secure password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        

        # Store the password in the session request for later reference
        session_request.password = password
        session_request.save()
        session_length = 10  # 10 seconds for testing

        # Start a new thread to delete the user after the session expires
        thread = threading.Thread(target=user_management.manage_user, args=(session_request.email, password, session_length)).start()
        
        print('session started !')

        # Redirect to a success page after saving the data
        return redirect('success_session_request', id=session_request.id)

    return render(request, 'app/session_request.html')

def session_redemand(request):
    if request.method == 'POST':
        email = request.POST['email']
        session_request = SessionRequest.objects.get(email=email)
        print('session redemanded !')
        # Generate a random secure password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        

        # Store the password in the session request for later reference
        session_request.password = password
        session_request.save()
        session_length = 10
        threading.Thread(target=user_management.redemand_session, args=(session_request.email, password, session_length)).start()
        return redirect('success_session_request', id=session_request.id)
    return render(request, 'app/session_redemand.html')

def success_session_request(request,id):
    session_request = SessionRequest.objects.get(pk=id)
    return render(request, 'app/success.html', {'session_request': session_request})



