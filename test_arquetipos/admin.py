from django.contrib import admin
from .models import Arquetipo, Pregunta, PersonajeMatch, SesionJugador

admin.site.register(Arquetipo)
admin.site.register(Pregunta)
admin.site.register(PersonajeMatch)

@admin.register(SesionJugador)
class SesionJugadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'arquetipo_resultado', 'edad', 'musica', 'cancion_resultado', 'fecha')
    list_filter = ('arquetipo_resultado', 'edad', 'musica', 'fecha')
    search_fields = ('nombre',)
