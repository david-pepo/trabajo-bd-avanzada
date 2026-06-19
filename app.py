import os
import re
import unicodedata
from flask import Flask, request, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# ==========================================
# FASE OFFLINE: PREPARACIÓN E INDEXACIÓN
# ==========================================

def limpiar_texto(texto):
    """Excluye signos de puntuación y tildes, pasando todo a minúsculas."""
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = texto.lower()
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto

carpeta_corpus = "corpus"
documentos_crudos = []
nombres_documentos = []

# Leer los 200 documentos de la carpeta
print(f"Cargando documentos desde la carpeta '{carpeta_corpus}'...")
if os.path.exists(carpeta_corpus):
    archivos = sorted(os.listdir(carpeta_corpus))
    for archivo in archivos:
        if archivo.endswith(".txt"):
            ruta = os.path.join(carpeta_corpus, archivo)
            with open(ruta, 'r', encoding='utf-8') as f:
                documentos_crudos.append(f.read())
                nombres_documentos.append(archivo)
else:
    print("Error: No se encontró la carpeta 'corpus'.")

# Limpiar y vectorizar (TF-IDF)
documentos_limpios = [limpiar_texto(doc) for doc in documentos_crudos]
vectorizador = TfidfVectorizer()
matriz_tfidf_docs = vectorizador.fit_transform(documentos_limpios)

print(f"✅ Fase Offline completada. {len(documentos_crudos)} documentos indexados y listos.")


# ==========================================
# FASE ONLINE: RUTAS WEB
# ==========================================

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/buscar', methods=['POST'])
def buscar():
    consulta_cruda = request.form.get('query')
    algoritmo = request.form.get('algoritmo')
    consulta_limpia = limpiar_texto(consulta_cruda)
    resultados = []

    if algoritmo == "vectorial":
        vector_consulta = vectorizador.transform([consulta_limpia])
        similitudes = cosine_similarity(vector_consulta, matriz_tfidf_docs)[0]
        
        for idx, score in enumerate(similitudes):
            if score > 0:
                resultados.append({
                    'titulo': nombres_documentos[idx],
                    'snippet': documentos_crudos[idx][:120] + "...",
                    'score': round(score, 4)
                })
                
    elif algoritmo == "bm25":
        resultados.append({
            'titulo': 'BM25 en construcción',
            'snippet': 'Falta programar la matemática de Okapi BM25 para comparar...',
            'score': 0.0
        })

    # Ordenar de mayor a menor similitud
    resultados.sort(key=lambda x: x['score'], reverse=True)

    return render_template('results.html', query=consulta_cruda, resultados=resultados, algoritmo=algoritmo)

# ==========================================
# NUEVA RUTA: VER DOCUMENTO Y RESALTAR
# ==========================================
@app.route('/documento/<nombre_archivo>')
def ver_documento(nombre_archivo):
    # Obtenemos la consulta de la URL para saber qué resaltar
    query = request.args.get('query', '')
    ruta = os.path.join(carpeta_corpus, nombre_archivo)
    
    if not os.path.exists(ruta):
        return "El documento no fue encontrado en el servidor.", 404
        
    with open(ruta, 'r', encoding='utf-8') as f:
        contenido = f.read()
        
    # Si hay una consulta, buscamos las palabras y las resaltamos
    if query:
        palabras_query = limpiar_texto(query).split()
        for palabra in palabras_query:
            if palabra:
                # Expresión regular para encontrar la palabra exacta y envolverla en <mark>
                contenido = re.sub(
                    rf'\b({palabra})\b', 
                    r'<mark style="background-color: #ffeb3b; padding: 2px; border-radius: 3px; font-weight: bold;">\1</mark>', 
                    contenido, 
                    flags=re.IGNORECASE
                )
                
    return render_template('documento.html', titulo=nombre_archivo, contenido=contenido, query=query)

if __name__ == '__main__':
    app.run(debug=True)