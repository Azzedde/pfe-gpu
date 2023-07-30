from django.urls import path
from django.urls import include
import app.views as views

urlpatterns = [
    path('', views.index, name='index'),
    path('success/<int:id>', views.success_session_request, name='success_session_request'),
   
]