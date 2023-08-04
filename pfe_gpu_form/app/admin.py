from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import SessionRequest, Etudiant

admin.site.register(SessionRequest)
admin.site.register(Etudiant)
