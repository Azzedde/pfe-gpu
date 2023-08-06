from django.shortcuts import render, HttpResponse


from django.shortcuts import render, redirect
from .models import SessionRequest, Etudiant
import random
import string
import os

import threading

from django.conf import settings
from django.core.mail import send_mail
from .tasks import send_email_task, start_user_session, create_user_task

from datetime import datetime, timedelta,time
import pytz

tz = pytz.timezone('Africa/Algiers')
def get_schedule(session_choice):
    # Define the session timings
    morning_start_time = time(7, 0)
    morning_end_time = time(14, 0)
    afternoon_start_time = time(14, 30)
    afternoon_end_time = time(23, 59)

    # Current date and time
    now = datetime.now()

    # Get the last session of the chosen type with status 'En attente'
    latest_session = SessionRequest.objects.filter(session_choice=session_choice, status='En attente').order_by('-date_debut').first()

    # If no such session is found, start with today's date; otherwise, use the day after the last session's start date
    if latest_session:
        date_debut = latest_session.date_debut.date() + timedelta(days=1)
    else:
        date_debut = now.date()

    # If session_choice is 'Matinale' and current time is past the session start, schedule for the next day
    if session_choice == 'Matinale':
        if now.date() == date_debut and now.time() >= morning_start_time:
            date_debut += timedelta(days=1)  # schedule for the next day
        
        date_debut_time = datetime.combine(date_debut, morning_start_time)
        date_fin = datetime.combine(date_debut, morning_end_time)

    # If session_choice is 'Après midi' and current time is past the session start, schedule for the next day
    else:
        if now.date() == date_debut and now.time() >= afternoon_start_time:
            date_debut += timedelta(days=1)  # schedule for the next day
        
        date_debut_time = datetime.combine(date_debut, afternoon_start_time)
        date_fin = datetime.combine(date_debut, afternoon_end_time)
    
    return date_debut_time, date_fin

def index(request):

    return render(request, 'app/index.html')


def session_request(request):
    # get number of sessions en attente
    nb_sessions_en_attente = SessionRequest.objects.filter(status='En attente').count()
    # get the form data to create a session and an etudiant
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
                #check if etudiant existed already in the database
        if Etudiant.objects.filter(email=email).exists():
            etudiant = Etudiant.objects.get(email=email)
            return redirect('erreur')
        etudiant.save()
        # create a user in the ubuntu system
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        create_user_task.delay(etudiant.email, password)
        print('compte crée !')

        # send an email to the student to confirm that his demand is being processed
        subject = "Demande de session en cours de traitement"
        body = f"Bonjour {nom} {prenom},\n\nNous avons bien reçu votre demande de session GPU.\n\nNous vous informons qu\'en ce moment il y a {nb_sessions_en_attente} demandes en attente.\n\nNous vous enverrons un email dès que votre session sera disponible.\n\nCordialement,\n\nService Réseaux ESI"
        send_email_task.delay(email, subject, body)

        # create a session request
        session_choice = request.POST['session_choice']
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
        send_email_task.delay(email, subject, body)
        

        # Calculate the time to run the task: 30 minutes before date_debut
        scheduled_time = date_debut - timedelta(minutes=30)

        # Use Celery's 'apply_async' with the 'eta' option to schedule the task
        send_email_task.apply_async(args=[email, subject, body], eta=scheduled_time)

        scheduled_start = session_request.date_debut
        result = start_user_session.apply_async(args=[etudiant.id, session_request.id], eta=scheduled_start)
        session_request.celery_task_id = result.id
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
        session_request = SessionRequest(etudiant=etudiant,
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
        send_email_task.delay(email, subject, body)
        # send an email in a thread to the student before 30 min of the date_debut of the session
        scheduled_time = date_debut - timedelta(minutes=30)
        send_email_task.apply_async(args=[email, subject, body], eta=scheduled_time)
        

        # Schedule the start of the session
        scheduled_start = session_request.date_debut
        result = start_user_session.apply_async(args=[etudiant.id, session_request.id], eta=scheduled_start)
        session_request.celery_task_id = result.id
        session_request.save()
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


def view_all_requests(request):
    session_requests = SessionRequest.objects.all()


    return render(request, 'app/view_all_requests.html', {'session_requests': session_requests})
