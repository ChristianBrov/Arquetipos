from django.db import models

class Arquetipo(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino (El)'),
        ('F', 'Femenino (La)'),
    ]
    nombre = models.CharField(max_length=100, unique=True)
    palabra_clave = models.CharField(max_length=100)
    genero_articulo = models.CharField(max_length=1, choices=GENERO_CHOICES, default='M')
    
    def __str__(self):
        articulo = "La" if self.genero_articulo == 'F' else "El"
        return f"{articulo} {self.nombre}"
class Pregunta(models.Model):
    TIPO_CHOICES = [
        ('ESCALA', 'Escala 1 a 5'),
        ('VISUAL', 'Imagen / Visual'),
    ]
    texto_pregunta = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='ESCALA')
    multiplicador = models.IntegerField(default=1) # 2 para las preguntas clave
    arquetipo_asociado = models.ForeignKey(Arquetipo, on_delete=models.CASCADE, related_name='preguntas')

    def __str__(self):
        return self.texto_pregunta

class PersonajeMatch(models.Model):
    EDAD_CHOICES = [
        ('< 20', 'Menor de 20'),
        ('20 a 30', '20 a 30 años'),
        ('31 a 40', '31 a 40 años'),
        ('41 a 50', '41 a 50 años'),
        ('> 50', 'Mayor de 50'),
    ]

    MUSICA_CHOICES = [
        ('Rock', 'Rock'),
        ('Urbano/Pop', 'Urbano/Pop'),
        ('Cumbia/Cuarteto', 'Cumbia/Cuarteto'),
        ('Electronica', 'Electrónica'),
        ('Folclore', 'Folclore'),
    ]

    # El arquetipo que obtuvo el usuario
    arquetipo = models.ForeignKey(Arquetipo, on_delete=models.CASCADE, related_name='matches_base', verbose_name="Tu Arquetipo")
    
    # El arquetipo con el que hace match (lista desplegable automática)
    arquetipo_match = models.ForeignKey(Arquetipo, on_delete=models.CASCADE, related_name='es_match_de', verbose_name="Hace match con (Complementario)", null=True)
    
    # Listas desplegables para edad y música
    rango_edad = models.CharField(max_length=50, choices=EDAD_CHOICES)
    genero_musical = models.CharField(max_length=50, choices=MUSICA_CHOICES)
    
    # Único texto libre
    cancion_identidad = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.arquetipo.nombre} + {self.arquetipo_match.nombre} ({self.rango_edad} / {self.genero_musical})"

class SesionJugador(models.Model):
    nombre = models.CharField(max_length=100)
    edad = models.CharField(max_length=50)
    genero = models.CharField(max_length=10, blank=True, null=True)
    musica = models.CharField(max_length=50)
    arquetipo_resultado = models.ForeignKey(Arquetipo, on_delete=models.CASCADE, null=True)
    cancion_resultado = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.arquetipo_resultado.nombre if self.arquetipo_resultado else 'Sin Resultado'} ({self.fecha.strftime('%d/%m/%Y %H:%M')})"

class PersonajeFamoso(models.Model):
    EDAD_CHOICES = [
        ('< 20', 'Menor de 20'),
        ('20 a 30', '20 a 30 años'),
        ('31 a 40', '31 a 40 años'),
        ('41 a 50', '41 a 50 años'),
        ('> 50', 'Mayor de 50'),
    ]
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    arquetipo = models.ForeignKey(Arquetipo, on_delete=models.CASCADE, related_name='famosos')
    rango_edad = models.CharField(max_length=50, choices=EDAD_CHOICES)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    nombre = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.nombre} ({self.arquetipo.nombre} - {self.rango_edad} - {self.genero})"

class PersonajeCrush(models.Model):
    arquetipo = models.ForeignKey(Arquetipo, on_delete=models.CASCADE, related_name='crushes')
    rango_edad = models.CharField(max_length=50)
    genero = models.CharField(max_length=1)
    nombre = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.nombre} (Crush {self.arquetipo.nombre} - {self.genero})"

class DescripcionArquetipo(models.Model):
    arquetipo = models.ForeignKey(Arquetipo, on_delete=models.CASCADE, related_name='descripciones')
    genero = models.CharField(max_length=1)  # 'M' o 'F'
    texto = models.TextField()

    def __str__(self):
        return f"Descripción {self.genero} para {self.arquetipo.nombre}"