import os
import random
import unicodedata
import re

# ==========================================
# 1. DICCIONARIOS TEMÁTICOS
# ==========================================
# Agregamos vocabularios con distintos temas para que el motor de búsqueda 
# tenga que esforzarse en diferenciar de qué habla cada documento.

tema_tecnologia = ["algoritmo", "computadora", "datos", "inteligencia", "artificial", "redes", "servidor", "python", "software", "hardware", "internet", "nube", "procesador", "memoria", "sistema", "programacion", "codigo", "base", "router", "ciberseguridad"]
tema_medicina = ["paciente", "medico", "hospital", "virus", "bacteria", "tratamiento", "sintoma", "diagnostico", "enfermedad", "vacuna", "salud", "clinica", "terapia", "cirugia", "medicamento", "infeccion", "receta", "farmacia", "dolor", "curacion"]
tema_deportes = ["pelota", "cancha", "jugador", "arbitro", "estadio", "torneo", "campeonato", "equipo", "entrenador", "partido", "gol", "atleta", "marcador", "victoria", "derrota", "olimpiadas", "entrenamiento", "competencia", "trofeo", "medalla"]
palabras_comunes = ["el", "la", "los", "las", "un", "una", "de", "con", "para", "por", "sobre", "entre", "este", "esta", "es", "son", "fue", "muy", "mucho", "poco", "y", "o", "pero", "porque"]

todos_los_temas = [tema_tecnologia, tema_medicina, tema_deportes]

# ==========================================
# 2. FUNCIÓN DE LIMPIEZA
# ==========================================
def limpiar_palabra(palabra):
    """Asegura que no haya tildes ni puntuación, cumpliendo la regla del PPT."""
    palabra = ''.join(c for c in unicodedata.normalize('NFD', palabra) if unicodedata.category(c) != 'Mn')
    palabra = re.sub(r'[^\w\s]', '', palabra)
    return palabra.lower()

# ==========================================
# 3. GENERADOR DE DOCUMENTOS
# ==========================================
def generar_corpus(cantidad_documentos=200, palabras_por_doc=500):
    # Crear carpeta 'corpus' si no existe
    carpeta = "corpus"
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
        print(f"Carpeta '{carpeta}' creada.")

    for i in range(cantidad_documentos):
        # Elegir un tema principal para este documento
        tema_principal = random.choice(todos_los_temas)
        
        documento = []
        for _ in range(palabras_por_doc):
            # 60% de probabilidad de usar el tema principal, 20% palabras comunes, 20% otros temas (ruido)
            probabilidad = random.random()
            
            if probabilidad < 0.60:
                palabra = random.choice(tema_principal)
            elif probabilidad < 0.80:
                palabra = random.choice(palabras_comunes)
            else:
                tema_secundario = random.choice(todos_los_temas)
                palabra = random.choice(tema_secundario)
                
            documento.append(limpiar_palabra(palabra))
        
        # Unir las palabras con espacios
        texto_final = " ".join(documento)
        
        # Guardar en un archivo txt (Ej: doc_001.txt, doc_002.txt...)
        nombre_archivo = os.path.join(carpeta, f"doc_{str(i+1).zfill(3)}.txt")
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(texto_final)
            
    print(f"✅ ¡Éxito! Se han generado {cantidad_documentos} documentos en la carpeta '{carpeta}'.")

# Ejecutar la función
if __name__ == "__main__":
    print("Iniciando generación de corpus...")
    generar_corpus()