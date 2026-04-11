import asyncio
import yfinance as yf
from newsapi import NewsApiClient
from groq import AsyncGroq
import json
import logging
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DEL ENTORNO ---
# Desactivar logs molestos de yfinance para mantener limpia la consola
yf.set_tz_cache_location("cache") 
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# --- APIS (Pon tus claves aquí) ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

# --- MÓDULO 1: DATOS DE MERCADO ---

def obtener_datos_accion(ticker, periodo="1mo"):
    """Descarga el historial de precios para la UI de Streamlit."""
    try:
        t = yf.Ticker(ticker)
        historial = t.history(period=periodo)
        if historial.empty: return None
        
        precio_actual = historial['Close'].iloc[-1]
        precio_ayer = historial['Close'].iloc[-2]
        variacion = ((precio_actual - precio_ayer) / precio_ayer) * 100
        
        return {
            "precio_actual": round(precio_actual, 2),
            "variacion_pct": round(variacion, 2)
        }
    except Exception:
        return None
        
def es_ticker_valido(ticker):
    """Validación rápida (Síncrona, se ejecutará en un hilo aparte)."""
    if not ticker or ticker == "NONE" or len(ticker) > 5:
        return False
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="1d", raise_errors=True)
        return not hist.empty
    except:
        return False

# --- MÓDULO 2: INTELIGENCIA ARTIFICIAL (ROBUSTA Y ENCAPSULADA) ---

async def extraer_ticker_ia(client, sem, titulo, descripcion):
    """Paso 1: NER (Reconocimiento de Entidades) Implacable."""
    prompt = f"""
    Actúa como un parser financiero automatizado.
    Noticia: {titulo} - {descripcion}
    
    TAREA: Extrae ÚNICAMENTE el Ticker oficial de bolsa americana (NASDAQ/NYSE) de la empresa principal afectada.
    REGLA 1: Si la noticia habla de un sector general (ej. "los semiconductores"), criptos genéricas, o no hay empresa cotizada, responde EXACTAMENTE: NONE.
    REGLA 2: No añades puntuación, texto, ni disculpas. SOLO el Ticker o NONE.
    """
    
    async with sem: # Protegemos la concurrencia
        for intento in range(3):
            try:
                res = await client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant",
                    temperature=0.0, # Determinismo máximo
                    max_tokens=10
                )
                texto = res.choices[0].message.content.strip().upper()
                ticker = texto.replace(".", "").replace('"', '').replace("'", "")
                return ticker if 1 <= len(ticker) <= 5 else "NONE"
            except Exception as e:
                # Manejo de Rate Limits (429) con Exponential Backoff
                if "429" in str(e): await asyncio.sleep((intento + 1) * 2)
                else: await asyncio.sleep(1)
        return "NONE"

async def analizar_amara_ia(client, sem, ticker, titulo, descripcion):
    """Paso 2: Prompt Avanzado - Analista Hedge Fund."""
    prompt = f"""
    Eres el Analista Cuantitativo Jefe de un Hedge Fund. Eres implacable, escéptico ante el marketing corporativo y detectas burbujas rápidamente.
    Evalúa esta noticia sobre {ticker}: "{titulo} - {descripcion}"
    
    Usa la Ley de Amara para destruir el "Hype" mediático o identificar valor ignorado.
    - Hype (70-100): Burbuja, FOMO, palabras de moda (AI, Quantum, Revolucionario) sin métricas reales hoy. Sobreestimación a corto plazo.
    - Hype (0-40): Desarrollos aburridos pero estructurales (patentes, infraestructura, regulaciones). Subestimación a largo plazo.
    
    Devuelve ÚNICAMENTE un JSON válido:
    {{
        "sentimiento": "Positivo" | "Negativo" | "Neutro",
        "nivel_hype": <Entero entre 0 y 100>,
        "fase_amara": "Sobreestimación a Corto Plazo" | "Subestimación a Largo Plazo" | "Expectativas Equilibradas" | "Ruido Irrelevante",
        "razon": "<Tu tesis cínica y brutalmente honesta en exactamente 1 frase de máximo 20 palabras>"
    }}
    """
    
    async with sem:
        for intento in range(3):
            try:
                res = await client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant",
                    temperature=0.1, 
                    max_tokens=200,
                    response_format={"type": "json_object"} # Fuerza output en JSON
                )
                return json.loads(res.choices[0].message.content)
            except Exception as e:
                if "429" in str(e): await asyncio.sleep((intento + 1) * 2)
                else: await asyncio.sleep(1)
        return None

async def procesar_noticia(articulo, client, sem):
    """Pipeline completo de una sola noticia."""
    if not articulo.get('description'): return None

    # 1. Extracción (Rápido)
    ticker = await extraer_ticker_ia(client, sem, articulo['title'], articulo['description'])
    if ticker == "NONE": return None

    # 2. Validación de ticker (Delega a un hilo síncrono para no bloquear el Loop)
    es_real = await asyncio.to_thread(es_ticker_valido, ticker)
    if not es_real: return None

    # 3. Análisis Profundo (Solo gasta tokens si el ticker existe)
    analisis = await analizar_amara_ia(client, sem, ticker, articulo['title'], articulo['description'])
    if not analisis: return None
    
    return {
        "titulo": articulo['title'],
        "fuente": articulo['source']['name'],
        "ticker_relacionado": ticker,
        "ia_sentimiento": analisis.get('sentimiento', 'Neutro'),
        "ia_hype": analisis.get('nivel_hype', 50),
        "ia_fase": analisis.get('fase_amara', 'Desconocida'),
        "ia_razon": analisis.get('razon', 'Sin análisis detallado')
    }

async def flujo_principal_async(articulos):
    """
    CEREBRO DE CONCURRENCIA: 
    Aquí instanciamos el Cliente y el Semáforo DENTRO del Event Loop activo.
    Esto soluciona el bloqueo de la segunda ejecución.
    """
    client = AsyncGroq(api_key=GROQ_API_KEY, timeout=45.0)
    sem = asyncio.Semaphore(4) # Procesa máximo 4 noticias en paralelo
    
    tareas = [procesar_noticia(art, client, sem) for art in articulos]
    # return_exceptions=True evita que si falla 1 noticia, se cancele todo
    resultados = await asyncio.gather(*tareas, return_exceptions=True)
    return [r for r in resultados if isinstance(r, dict)]

def obtener_noticias_ia(tema_busqueda):
    """Punto de entrada síncrono llamado por Streamlit."""
    print(f"\n📡 Buscando noticias sobre: {tema_busqueda}...")
    fecha_desde = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    
    try:
        all_articles = newsapi.get_everything(
            q=tema_busqueda, 
            from_param=fecha_desde, 
            language='en', 
            sort_by='relevancy', 
            page_size=12 # Traemos 12, filtramos la morralla, nos quedamos ~4
        )
        articulos = all_articles.get('articles', [])
    except Exception as e:
        print(f"Error NewsAPI: {e}")
        return []

    try:
        # Creamos y destruimos el Event Loop limpiamente por CADA ejecución
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        noticias_validas = loop.run_until_complete(flujo_principal_async(articulos))
        loop.close()
    except Exception as e:
        print(f"Error Crítico Async: {e}")
        return []
        
    return noticias_validas[:4]
