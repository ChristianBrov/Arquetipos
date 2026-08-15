from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('test_arquetipos.urls')), # Esto conecta nuestra app al inicio
]