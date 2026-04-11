# FirstFolio 🔭 | Plataforma de Inteligencia Financiera con IA

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)
![Groq](https://img.shields.io/badge/LLM-Groq_(Llama_3)-black.svg)
![Status](https://img.shields.io/badge/Status-MVP_Finalizado-brightgreen.svg)

**FirstFolio** es una plataforma híbrida (educativa y analítica) diseñada para democratizar la inversión y proteger al inversor *retail* (minorista) del ruido mediático. Utiliza Inteligencia Artificial Generativa y modelos cuantitativos de riesgo para ofrecer una transición guiada desde la teoría financiera básica hasta la toma de decisiones informada.

🔗 **[Prueba la aplicación en vivo aquí]** *(Nota: Reemplaza este texto con tu enlace de Streamlit Cloud cuando lo tengas)*

---

## 🚀 Características Principales

La aplicación se divide en tres módulos principales:

### 1. Radar Cuantitativo de Sentimiento (IA + Ley de Amara)
Un motor de Procesamiento de Lenguaje Natural (NLP) impulsado por **Llama-3 (vía Groq API)** que ingesta noticias financieras en tiempo real.
* **Extracción Inteligente (NER):** Identifica automáticamente el Ticker bursátil afectado.
* **Filtro de Hype (Ley de Amara):** Analiza el texto para detectar si la noticia es puro FOMO (Riesgo de Sobreestimación a Corto Plazo) o si tiene valor estructural ignorado, puntuando el *Hype* de 0 a 100.
* **Concurrencia:** Utiliza `asyncio` para procesar múltiples noticias en paralelo sin cuellos de botella.

### 2. Monitor de Riesgo Macro (RVM 4.2)
Un algoritmo cuantitativo que evalúa la salud del mercado global.
* Analiza divisas de LatAm, Asia y el G10 usando datos históricos de `yfinance`.
* Calcula la **Volatilidad Asimétrica** y el *Downside Risk* para generar un **IV Score** (Índice de Vulnerabilidad).
* Visualización avanzada con mapas de calor y gráficos de radar interactivos (Plotly).

### 3. Aula Virtual & Simuladores Interactivos
Entorno de *microlearning* para enseñar conceptos financieros desde cero.
* Explicación de la inflación, acciones vs. ETFs y criterios ASG.
* **Simulador de Órdenes:** Permite interactuar con el *Bid/Ask* simulando órdenes a Mercado y Limitadas.
* **Simulador de Shock de Mercado:** Demuestra visual y matemáticamente el poder de la diversificación (Acción individual vs. ETF sectorial) ante reportes de ganancias negativos.

---

## 🛠️ Arquitectura y Tecnologías (Tech Stack)

* **Frontend:** [Streamlit](https://streamlit.io/)
* **Backend & Concurrencia:** Python (`asyncio`, `aiohttp`)
* **Modelos LLM:** [Groq API](https://groq.com/) (Llama-3.1-8b-instant)
* **Ingesta de Datos:** `NewsAPI` (Noticias), `yfinance` (Cotizaciones en vivo)
* **Análisis Cuantitativo:** `pandas`, `numpy`, `scipy`
* **Visualización:** `plotly`
