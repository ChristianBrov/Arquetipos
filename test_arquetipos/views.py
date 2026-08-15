import random
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Pregunta, Arquetipo, PersonajeMatch, SesionJugador, PersonajeFamoso, PersonajeCrush, DescripcionArquetipo 

def inicio(request):
    if request.method == 'POST':
        # Guardamos los datos del usuario en la sesión
        request.session['usuario_nombre'] = request.POST.get('nombre')
        request.session['usuario_edad'] = request.POST.get('edad')
        request.session['usuario_musica'] = request.POST.get('musica')
        request.session['usuario_genero'] = request.POST.get('genero')
        request.session['partida_guardada'] = False
        
        # SELECCIÓN MIXTA: 10 preguntas normales + 2 íntimas (multiplicador 0)
        normales = list(Pregunta.objects.filter(multiplicador__gt=0).values_list('id', flat=True))
        intimas = list(Pregunta.objects.filter(multiplicador=0).values_list('id', flat=True))
        
        # Seleccionamos al azar de cada pool asegurando la mezcla perfecta
        sample_normales = random.sample(normales, min(len(normales), 10)) if normales else []
        sample_intimas = random.sample(intimas, min(len(intimas), 2)) if intimas else []
        
        selected_ids = sample_normales + sample_intimas
        random.shuffle(selected_ids) # Mezclamos para que las íntimas salgan de forma sorpresiva
        
        # Si por alguna razón hay pocas cargadas en total, unificamos con lo que haya
        if not selected_ids:
            all_ids = list(Pregunta.objects.values_list('id', flat=True))
            selected_ids = random.sample(all_ids, min(len(all_ids), 12))
            
        # Guardamos la lista de IDs y reiniciamos el contador de pasos en la sesión
        request.session['preguntas_ids'] = selected_ids
        request.session['paso_actual'] = 0
        request.session['puntajes'] = {str(a.id): 0 for a in Arquetipo.objects.all()}
        
        return redirect('test_preguntas')
        
    return render(request, 'test_arquetipos/inicio.html')

def test_preguntas(request):
    nombre = request.session.get('usuario_nombre')
    
    # Si no puso su nombre, lo mandamos de vuelta al inicio por seguridad
    if not nombre:
        return redirect('inicio')
        
    preguntas_ids = request.session.get('preguntas_ids', [])
    paso = request.session.get('paso_actual', 0)
    
    # Si por alguna razón la lista está vacía, la volvemos a generar
    if not preguntas_ids:
        normales = list(Pregunta.objects.filter(multiplicador__gt=0).values_list('id', flat=True))
        intimas = list(Pregunta.objects.filter(multiplicador=0).values_list('id', flat=True))
        
        sample_normales = random.sample(normales, min(len(normales), 10)) if normales else []
        sample_intimas = random.sample(intimas, min(len(intimas), 2)) if intimas else []
        
        selected_ids = sample_normales + sample_intimas
        random.shuffle(selected_ids)
        
        if not selected_ids:
            all_ids = list(Pregunta.objects.values_list('id', flat=True))
            if not all_ids:
                return HttpResponse("Por favor, cargá algunas preguntas desde el panel de administración (/admin).")
            selected_ids = random.sample(all_ids, min(len(all_ids), 12))
            
        request.session['preguntas_ids'] = selected_ids
        request.session['paso_actual'] = 0
        preguntas_ids = selected_ids
        paso = 0

    # Si ya respondió todas, vamos al resultado
    if paso >= len(preguntas_ids):
        return redirect('resultado_final')
        
    pregunta_actual = Pregunta.objects.get(id=preguntas_ids[paso])
    
    if request.method == 'POST':
        valor_respuesta = int(request.POST.get('respuesta', 3))
        arquetipo_id = str(pregunta_actual.arquetipo_asociado.id)
        
        # Multiplicador 0 para las preguntas íntimas no suma puntos
        puntos_a_sumar = valor_respuesta * pregunta_actual.multiplicador
        
        puntajes = request.session.get('puntajes', {})
        puntajes[arquetipo_id] = puntajes.get(arquetipo_id, 0) + puntos_a_sumar
        request.session['puntajes'] = puntajes
        
        request.session['paso_actual'] = paso + 1
        return redirect('test_preguntas')

    context = {
        'nombre': nombre,
        'pregunta': pregunta_actual,
        'numero_pregunta': paso + 1,
        'total_preguntas': len(preguntas_ids),
        'progreso': int(((paso + 1) / len(preguntas_ids)) * 100)
    }
    return render(request, 'test_arquetipos/preguntas.html', context)

def resultado_final(request):
    nombre = request.session.get('usuario_nombre', 'Viajero')
    edad_usuario = request.session.get('usuario_edad', '20 a 30')
    musica_usuario = request.session.get('musica', 'Rock')
    genero_usuario = request.session.get('usuario_genero', 'M')
    puntajes = request.session.get('puntajes', {})
    
    arquetipo_ganador_obj = None
    if puntajes:
        mejor_id = max(puntajes, key=puntajes.get)
        try:
            arquetipo_ganador_obj = Arquetipo.objects.get(id=int(mejor_id))
        except Arquetipo.DoesNotExist:
            pass

    # ---------- NUEVA LÓGICA DE GÉNERO ----------
    nombre_mostrar = ""
    if arquetipo_ganador_obj:
        nombre_base = arquetipo_ganador_obj.nombre.strip().upper()
        
        if genero_usuario == 'F':
            nombres_femeninos = {
                "GUARDIAN": "LA GUARDIANA",
                "EXPLORADOR": "LA EXPLORADORA",
                "VISIONARIO": "LA VISIONARIA",
                "IMPULSOR": "LA IMPULSORA",
                "ANALISTA": "LA ANALISTA",
                "ESTRATEGA": "LA ESTRATEGA"
            }
            nombre_mostrar = nombres_femeninos.get(nombre_base, f"LA {nombre_base}")
        else:
            nombres_masculinos = {
                "GUARDIAN": "EL GUARDIAN",
                "EXPLORADOR": "EL EXPLORADOR",
                "VISIONARIO": "EL VISIONARIO",
                "IMPULSOR": "EL IMPULSOR",
                "ANALISTA": "EL ANALISTA",
                "ESTRATEGA": "EL ESTRATEGA"
            }
            nombre_mostrar = nombres_masculinos.get(nombre_base, f"EL {nombre_base}")
    # --------------------------------------------

    # 1. Buscamos el Dúo Dinámico aleatorio
    duo_encontrado = None
    if arquetipo_ganador_obj:
        duo_encontrado = PersonajeMatch.objects.filter(
            arquetipo=arquetipo_ganador_obj,
            rango_edad=edad_usuario,
            genero_musical=musica_usuario
        ).order_by('?').first()

    # 2. Buscamos el Famoso aleatorio
    famoso_encontrado = None
    if arquetipo_ganador_obj:
        famoso_encontrado = PersonajeFamoso.objects.filter(
            arquetipo=arquetipo_ganador_obj,
            rango_edad=edad_usuario,
            genero=genero_usuario
        ).order_by('?').first()

    # 3. Buscamos el Crush aleatorio (Género opuesto)
    crush_encontrado = None
    if duo_encontrado and genero_usuario:
        genero_opuesto = 'F' if genero_usuario == 'M' else 'M'
        crush_encontrado = PersonajeCrush.objects.filter(
            arquetipo=duo_encontrado.arquetipo_match,
            rango_edad=edad_usuario,
            genero=genero_opuesto
        ).order_by('?').first()

    # 4. Buscamos la descripción aleatoria según el género del usuario
    descripcion_dinamica = None
    if arquetipo_ganador_obj and genero_usuario:
        descripcion_dinamica = DescripcionArquetipo.objects.filter(
            arquetipo=arquetipo_ganador_obj,
            genero=genero_usuario
        ).order_by('?').first()

    # Guardado en historial
    if arquetipo_ganador_obj and not request.session.get('partida_guardada'):
        SesionJugador.objects.create(
            nombre=nombre,
            edad=edad_usuario,
            genero=genero_usuario,
            musica=musica_usuario,
            arquetipo_resultado=arquetipo_ganador_obj,
            cancion_resultado=duo_encontrado.cancion_identidad if duo_encontrado else "Sin canción"
        )
        request.session['partida_guardada'] = True

    # Render final
    return render(request, 'test_arquetipos/resultado.html', {
        'nombre': nombre,
        'arquetipo': arquetipo_ganador_obj,
        'nombre_mostrar': nombre_mostrar,  # <-- Enviamos el nombre corregido al template
        'descripcion': descripcion_dinamica,
        'duo': duo_encontrado,
        'famoso': famoso_encontrado,
        'crush': crush_encontrado
    })