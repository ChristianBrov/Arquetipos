from django.urls import path
from . import views

urlpatterns = [
        path('', views.inicio, name='inicio'),
        path('test/', views.test_preguntas, name='test_preguntas'),
        path('resultado/', views.resultado_final, name='resultado_final'),
]