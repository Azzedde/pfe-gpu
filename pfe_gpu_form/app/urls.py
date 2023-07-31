from django.urls import path
from django.urls import include
import app.views as views

urlpatterns = [
    path('', views.index, name='index'),
    path('session_request/', views.session_request, name='session_request'),
    path('session_redemand', views.session_redemand, name='session_redemand'),
    path('success/<int:id>', views.success_session_request, name='success_session_request'),
   
]