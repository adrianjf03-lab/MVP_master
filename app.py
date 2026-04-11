
import streamlit as st
import motor_datos  
import rvm_logic    

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="FirstFolio", page_icon="🔭", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #00e5ff !important; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    div[data-testid="stExpander"] { background-color: #1a1f25; border: 1px solid #30363d; border-radius: 8px; }
    .sentimiento-positivo { color: #2ea043; font-weight: 800; background-color: rgba(46, 160, 67, 0.15); padding: 2px 8px; border-radius: 12px;}
    .sentimiento-negativo { color: #f85149; font-weight: 800; background-color: rgba(248, 81, 73, 0.15); padding: 2px 8px; border-radius: 12px;}
    .sentimiento-neutro { color: #8b949e; font-weight: 800; background-color: rgba(139, 148, 158, 0.15); padding: 2px 8px; border-radius: 12px;}
    .tesis-box { border-left: 4px solid #00e5ff; padding-left: 15px; margin-top: 10px; font-style: italic; color: #c9d1d9; }
</style>
""", unsafe_allow_html=True)

# --- MEMORIA DE SESIÓN (Caché interactiva) ---
if "noticias_cache" not in st.session_state:
    st.session_state.noticias_cache = {}

# --- SIDEBAR ---
with st.sidebar:
    st.title("FirstFolio 🔭")
    st.caption("Plataforma de Inteligencia Financiera")
    st.info("MVP con integración de IA Generativa (LLMs) y Análisis Estructural.")

# --- NAVEGACIÓN ---
tab1, tab2, tab3 = st.tabs(["🚀 Radar de Oportunidades (IA)", "🌍 Monitor de Riesgo (RVM)", "🎓 Aula Virtual"])

# === PESTAÑA 1: NOTICIAS E IA REAL ===
with tab1:
    st.header("Radar Cuantitativo de Sentimiento")
    st.markdown("Agentes de IA analizando el impacto mediático (Hype) vs. Valor Real.")
    
    # Integración Sección D (Explicación IA contextual)
    with st.expander("ℹ️ ¿Cómo funciona nuestro Motor de IA? (Combatiendo el Ruido Mediático)"):
        st.write("""
        El mercado se mueve por noticias, pero no todo lo que brilla es oro. FirstFolio integra un motor de Inteligencia Artificial que escanea noticias tecnológicas mundiales para ayudarte a tomar decisiones sin dejarte llevar por las emociones.
        * **Semáforo de Sentimiento:** Nuestra IA lee las noticias y te indica si el impacto para un activo específico es Positivo, Neutro o Negativo.
        * **El Nivel de Hype (Ley de Amara):** Los humanos tendemos a sobrestimar el impacto de una tecnología a corto plazo y a subestimarlo a largo plazo. Nuestro sistema mide el "Nivel de Hype" (0-100) para evitar que compres en el pico de la euforia mediática, justo antes de que el precio caiga.
        """)

    opciones_tema = {
        "Inteligencia Artificial": "Artificial Intelligence",
        "Semiconductores": "Semiconductors",
        "Blockchain": "Cryptocurrency",
        "Vehículos Eléctricos": "Electric Vehicles"
    }
    
    c1, c2 = st.columns([3, 1])
    with c1:
        tema_es = st.selectbox("Selecciona Sector para Escanear:", list(opciones_tema.keys()), label_visibility="collapsed")
        tema_en = opciones_tema[tema_es]
    with c2:
        escanear_btn = st.button("📡 Escanear Mercado", use_container_width=True, type="primary")
    
    if escanear_btn:
        with st.spinner(f"Agentes procesando {tema_es} en paralelo... esto tomará unos segundos."):
            resultados = motor_datos.obtener_noticias_ia(tema_en)
            st.session_state.noticias_cache[tema_en] = resultados

    if tema_en in st.session_state.noticias_cache:
        noticias = st.session_state.noticias_cache[tema_en]
        
        if not noticias:
            st.warning("La IA no encontró empresas cotizadas claras en las noticias recientes de este sector.")
        else:
            st.markdown("---")
            col_news, col_data = st.columns([6, 4])
            
            with col_news:
                st.subheader("📰 Flujo de Análisis")
                for noti in noticias:
                    with st.container():
                        st.markdown(f"**{noti['titulo']}**")
                        st.caption(f"Fuente: {noti['fuente']} | Ticker Extraído: `{noti['ticker_relacionado']}`")
                        
                        color_clase = f"sentimiento-{noti['ia_sentimiento'].lower()}"
                        
                        with st.expander("🔬 Veredicto del Analista (Ley de Amara)", expanded=False):
                            st.markdown(f"Sentimiento del Mercado: <span class='{color_clase}'>{noti['ia_sentimiento'].upper()}</span>", unsafe_allow_html=True)
                            
                            try:
                                hype = max(0, min(100, int(noti['ia_hype'])))
                            except:
                                hype = 50 
                            
                            st.write("")
                            if hype > 70:
                                st.progress(hype, text=f"🔥 Hype: {hype}/100 ➔ ⚠️ Riesgo FOMO / Sobreestimación Corto Plazo")
                            elif hype < 40:
                                st.progress(hype, text=f"🧊 Hype: {hype}/100 ➔ 🌱 Posible Subestimación Largo Plazo")
                            else:
                                st.progress(hype, text=f"⚖️ Hype: {hype}/100 ➔ Expectativas Equilibradas")
                            
                            st.markdown(f"**Fase Detectada:** `{noti['ia_fase']}`")
                            st.markdown(f"<div class='tesis-box'><b>Tesis de la IA:</b> {noti['ia_razon']}</div>", unsafe_allow_html=True)
                        st.write("") 

            with col_data:
                st.subheader("📊 Cotización en Vivo")
                for noti in noticias:
                    ticker = noti['ticker_relacionado']
                    datos = motor_datos.obtener_datos_accion(ticker)
                    if datos:
                        st.metric(label=f"Acción: {ticker}", value=f"${datos['precio_actual']}", delta=f"{datos['variacion_pct']}% (24h)")
                    else:
                        st.metric(label=f"Acción: {ticker}", value="No disp.", delta="-")

# === PESTAÑA 2: RIESGO MACRO (RVM 4.2) ===
with tab2:
    st.header("Radar de Vulnerabilidad Macro (RVM 4.2)")
    st.markdown("Este módulo utiliza **Volatilidad Asimétrica** para detectar crisis estructurales.")
    st.info("💡 **Tip FirstFolio:** Antes de operar, revisa este mapa de calor. Te muestra el riesgo estructural de los mercados globales. ¡Si el mercado entero está en rojo, opera con cautela!")
    
    if st.button("🔄 Ejecutar Escáner de Riesgo Global"):
        with st.spinner("Procesando IV Scores..."):
            df = rvm_logic.analitics.obtener_datos()
            if not df.empty:
                df_proc = rvm_logic.analitics.calcular_iv_score(df)
                top_risk = df_proc.sort_values('IV_Score', ascending=False).iloc[0]
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Mayor Riesgo Detectado", top_risk['Pais'], f"IV: {top_risk['IV_Score']}")
                c2.metric("Nivel de Alerta", top_risk['Senal'])
                c3.metric("Tendencia", top_risk['Tendencia'])
                
                fig_map, fig_radar = rvm_logic.analitics.generar_graficos(df_proc)
                col_g1, col_g2 = st.columns([3, 2])
                with col_g1: st.plotly_chart(fig_map, width="stretch")
                with col_g2: st.plotly_chart(fig_radar, width="stretch")
                
                with st.expander("📂 Ver Matriz de Datos Completa"):
                    st.dataframe(df_proc[['Pais', 'IV_Score', 'Senal', 'Vol_Asim', 'Devaluacion', 'Tendencia', 'R2']].style.background_gradient(subset=['IV_Score'], cmap='RdYlGn_r'))

# === PESTAÑA 3: AULA VIRTUAL ===
with tab3:
    st.header("🎓 Aula Virtual: El Mercado de Valores y tu Primera Operativa")
    st.markdown("**Público Objetivo:** Inversores noveles de España y América Latina.")
    st.info("Enfoque: Aprendizaje interactivo, prevención del riesgo (Ley de Amara) y simulación de operativa real.")

    # MÓDULO 1: Fusión de la Inflación y el Ecosistema
    with st.expander("🧱 Módulo 1: La Base de Todo y el Ecosistema Bursátil"):
        st.write("""
        Para entender la inversión, primero debemos entender a su mayor enemigo: **La Inflación**.
        
        Imagina que el dinero es como un cubito de hielo en tu mano. Si te quedas quieto y lo guardas debajo del colchón, el calor de la habitación (la inflación) hará que se derrita lentamente. Cada año, con el mismo billete, puedes comprar menos cosas porque todo se vuelve más caro.
        
        **¿Qué es entonces invertir?**
        Es coger ese hielo y meterlo en un congelador, o mejor aún, usar el agua para plantar un árbol que te dé manzanas todos los años. Invertir es poner a tu dinero a trabajar para ti, generando rendimientos que superen a la inflación.
        
        #### 🌍 El Ecosistema: ¿Quiénes participan en este proceso?
        No necesitas ser millonario para ser socio de las grandes empresas del mundo. Para que este mercado funcione de forma segura, existen varios participantes clave:
        * **Emisoras:** Empresas o gobiernos que buscan financiación ofreciendo una parte de su capital (acciones) o emitiendo deuda.
        * **Inversores:** Personas como tú (inversores minoristas) o grandes fondos que aportan su capital buscando un rendimiento.
        * **Intermediarios (Brókers / Agencias de Valores):** Son las únicas entidades autorizadas para conectar a los inversores con el mercado.
        * **Bolsas de Valores:** Los mercados organizados donde ocurre la magia (ej. BME en España, BMV o BIVA en México).
        * **Reguladores:** El "árbitro" del juego que protege tus derechos (ej. la CNMV en España o la CNBV en México).
        
        #### 📌 Ejemplos del día a día:
        * **Ejemplo (El cine):** Pregúntale a tus abuelos cuánto costaba una entrada de cine hace 40 años. Hoy cuesta muchísimo más. El billete es el mismo, pero vale menos. Eso es la inflación robando tus ahorros en cámara lenta.
        
        #### 🛑 Mitos comunes:
        * **Mito:** *"Guardar el dinero en la cuenta del banco es lo más seguro"*. 
          **Verdad:** Es el único lugar donde tienes la certeza matemática de perder dinero a largo plazo, porque el interés del banco suele ser menor que la inflación.
        """)

    # MÓDULO 2: Se mantiene intacto (Excelente pedagogía)
    with st.expander("🏛️ Módulo 2: ¿Qué es el Mercado de Valores en realidad?"):
        st.write("""
        A menudo vemos la Bolsa de Valores como una pantalla llena de números rojos y verdes incomprensibles, o en las películas lo pintan como un casino donde la gente grita y apuesta. Pero su función real es muy lógica, aburrida y necesaria.
        
        Imagina un mercado de agricultores gigante. Por un lado, hay emprendedores que tienen grandes ideas pero necesitan dinero para construir fábricas (las **empresas**). Por otro lado, hay personas normales que tienen dinero ahorrado y quieren hacerlo crecer (los **inversores**). 
        
        El mercado de valores es el puente regulado y seguro que conecta a ambos. Cuando inviertes, **estás comprando pequeños pedacitos de empresas reales**.
        
        #### 📌 Ejemplos del día a día:
        * **Ejemplo 1 (El puesto de limonada):** Imagina que tienes un puesto de limonada exitoso, pero quieres abrir 10 puestos más y no tienes dinero. Vendes el 50% de tu negocio a un amigo por $100. Si triunfan, tu amigo se lleva la mitad de las ganancias. La Bolsa es exactamente esto, a escala mundial.
        * **Ejemplo 2 (La Pizza):** Piensa en la empresa Apple como si fuera una pizza gigante cortada en millones de porciones diminutas. Cuando compras una acción, estás comprando una porción de esa pizza.
        
        #### 🛑 Mitos comunes:
        * **Mito:** *"La bolsa es como ir al casino, todo depende de la suerte"*. 
          **Verdad:** En un casino, las matemáticas están diseñadas para que la casa gane. En la bolsa, si compras partes de buenas empresas, participas en el crecimiento real de la economía mundial.
        """)

    # MÓDULO 3: Fusión de las analogías antiguas con los nuevos instrumentos
    with st.expander("🍎 Módulo 3: El Menú del Inversor (Tu Arsenal)"):
        st.write("""
        Antes de entrar al simulador, debes conocer qué puedes comprar. **La regla de oro es: A mayor riesgo, mayor rendimiento potencial.**
        
        #### Ruta 1: Renta Variable (Para crecer tu capital asumiendo riesgo)
        * **Acciones Individuales (Stocks):** Te conviertes en propietario de una fracción de la empresa. El riesgo está 100% concentrado.
          * *Analogía:* Gastar todo tu presupuesto en una sola manzana gigante. Si sale podrida, pierdes.
        * **ETFs (Fondos Cotizados):** Son "canastas" que agrupan muchas acciones y cotizan en bolsa. Te permiten invertir en sectores enteros.
          * *Analogía:* Comprar una cesta surtida con manzanas, plátanos y uvas. Si una fruta sale mala, no importa casi nada, porque las demás te salvan la cena. A esta magia se le llama **Diversificación**.
        * **Sector Inmobiliario (SOCIMIs o FIBRAS):** Vehículos para invertir en grandes inmuebles (centros comerciales, oficinas) y recibir ganancias por los alquileres, combinando características de deuda y capital.
        
        #### Ruta 2: Renta Fija (Para proteger tu capital)
        * **Deuda Gubernamental:** Le prestas tu dinero al gobierno de tu país (ej. Letras del Tesoro en España, Cetes en México) a cambio de un interés fijo. Es la inversión de menor riesgo.
        
        #### 🛑 Mitos comunes:
        * **Mito:** *"Para ganar dinero de verdad, tengo que encontrar en secreto al nuevo Google o Amazon"*. 
          **Verdad:** Es casi imposible predecir eso. La inmensa mayoría de los millonarios invierten en ETFs diversificados y ganan dinero de forma lenta pero constante.
        """)

    # MÓDULO 4: Se mantiene la teoría y se inyecta el Simulador 1
    with st.expander("⚙️ Módulo 4: La Mecánica del Mercado (Cómo Comprar)"):
        st.write("""
        Cuando entres a la app de tu banco o a tu *broker*, verás siempre dos precios parpadeando:
        
        * **Bid (Precio de Compra / Oferta):** Es el precio máximo que un comprador está dispuesto a pagar. Es lo que tú recibes si quieres vender.
        * **Ask (Precio de Venta / Demanda):** Es el precio mínimo por el cual un vendedor está dispuesto a soltar su activo. Es el precio que tú pagas al comprar.
        * 💡 *Tip FirstFolio: La diferencia entre el Ask y el Bid se llama Spread.*
        
        Tienes formas principales de lanzar tu orden:
        1. **Orden a Mercado (Market Order):** Le dices al broker: *"¡Cómpralo YA!"*. Se ejecuta inmediatamente al mejor precio disponible (priorizas rapidez).
        2. **Orden Limitada (Limit Order):** Le dices al broker: *"Solo compro si el precio baja a X cantidad"*. Te asegura no pagar más de lo que deseas, pero la orden puede no ejecutarse nunca.
        3. **Stop-Loss (Parada de pérdidas):** Es tu cinturón de seguridad. Si compras a $50 y configuras el Stop a $45, el sistema vende automáticamente si el precio cae a $45 para evitar que pierdas más.
        
        #### 📌 Ejemplos del día a día:
        * **Ejemplo (Comprar un coche):** Si usas una "Orden a mercado", ves el coche a $10,000 y dices "Lo compro ya, toma el dinero". Si usas una "Orden limitada", le dices al vendedor: "Solo te doy $9,000. Llámame si aceptas".
        """)
        
        st.markdown("---")
        st.subheader("🎮 Primera Misión del Simulador: Ejecuta tu compra")
        st.info("Observa el Bid y el Ask de la empresa ficticia TechFolio. Decide tu orden estratégica sin riesgo.")
        
        col_bid_1, col_ask_1 = st.columns(2)
        col_bid_1.metric("💰 BID (Compradores ofrecen)", "$99.50", delta_color="off")
        col_ask_1.metric("🏷️ ASK (Vendedores exigen)", "$100.50", delta_color="off")
        
        tipo_orden = st.radio("Elige tu instrucción para el Bróker:", ["A Mercado (Comprar YA)", "Limitada (Yo fijo precio máximo)"])
        precio_limite = 0.0
        if tipo_orden == "Limitada (Yo fijo precio máximo)":
            precio_limite = st.number_input("Precio máximo a pagar ($):", min_value=1.0, value=99.00, step=0.10)
            
        if st.button("🚀 Enviar Orden de Compra", type="primary", key="btn_m1"):
            if tipo_orden == "A Mercado (Comprar YA)":
                st.success("✅ **ORDEN EJECUTADA:** Compraste al instante por el precio Ask actual de **$100.50**.")
            else:
                if precio_limite >= 100.50:
                    st.success(f"✅ **ORDEN EJECUTADA:** Ofreciste ${precio_limite:.2f}, el sistema te consiguió el mejor precio disponible ($100.50).")
                else:
                    st.warning(f"⏳ **ORDEN PENDIENTE:** Los vendedores exigen $100.50. Tu oferta de ${precio_limite:.2f} queda a la espera en el libro de órdenes.")

    # MÓDULO 5: El Simulador de Shock (Acción vs ETF)
    with st.expander("🛡️ Módulo 5: Segunda Misión - El Duelo (Acción vs. ETF)"):
        st.write("""
        En el mundo real, no es lo mismo apostar todo tu dinero a una sola carta que repartirlo. Tu objetivo en esta sesión será simular un escenario de crisis sectorial (Un mal reporte de ganancias).
        * **Acción Individual:** Todo tu riesgo está concentrado. Si la empresa falla, sufres el impacto completo.
        * **ETF Sectorial:** Tienes una canasta de 100 empresas. Si una falla, las otras 99 amortiguan el golpe (Diversificación).
        """)
        
        st.markdown("---")
        st.subheader("💥 Simulador de Shock de Mercado")
        st.write("Imagina que inviertes $10,000 en una sola acción tecnológica y otros $10,000 en un ETF del mismo sector. De pronto, la empresa de la acción individual anuncia pérdidas masivas.")
        
        gravedad = st.slider("Selecciona la Gravedad del Reporte Negativo:", 1, 5, 3, help="1 = Leve, 5 = Pánico de Mercado")
        
        if st.button("Simular Impacto (Reporte de Ganancias)", type="primary", key="btn_m2"):
            # Lógica matemática para simular el impacto diferencial
            caida_accion = gravedad * 8.5  
            caida_etf = gravedad * 0.8     
            
            saldo_accion = 10000 * (1 - caida_accion/100)
            saldo_etf = 10000 * (1 - caida_etf/100)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="📉 Cartera 1: Acción Individual", value=f"${saldo_accion:,.2f}", delta=f"-{caida_accion:.1f}% Riesgo Concentrado", delta_color="inverse")
            with col2:
                st.metric(label="🛡️ Cartera 2: ETF Sectorial", value=f"${saldo_etf:,.2f}", delta=f"-{caida_etf:.1f}% Diversificado", delta_color="inverse")
                
            st.success("**Análisis de la IA:** Observa cómo el ETF te brinda diversificación instantánea. El mal desempeño de una sola empresa se compensa con la estabilidad de las otras 99 en la canasta, protegiendo tu capital.")

    # MÓDULO 6: Nueva sección ESG
    with st.expander("🌱 Módulo 6: Invierte con Propósito (Finanzas Sostenibles)"):
        st.write("""
        Hoy en día puedes buscar rendimientos mientras ayudas al planeta. Las inversiones **ASG** consideran tres criterios fundamentales:
        * **A (Ambientales):** Lucha contra el cambio climático, reducción de emisiones y uso de energías limpias.
        * **S (Sociales):** Respeto a los derechos humanos, condiciones laborales justas y diversidad.
        * **G (Gobernanza):** Transparencia empresarial, ética directiva y anticorrupción.
        
        Podrás encontrar instrumentos como **Bonos Verdes** o **ETFs Sustentables** que financian proyectos de impacto positivo.
        """)

    # MÓDULO 7: Las Reglas de Oro intactas
    with st.expander("🛑 Módulo 7: Tus 3 Reglas de Oro para Sobrevivir"):
        st.write("""
        Antes de ir a la pestaña del **Radar de Oportunidades** y empezar a analizar noticias reales, grábate a fuego estas reglas:
        
        #### 🥇 Regla 1: Invierte dinero que no necesites mañana
        La bolsa fluctúa constantemente. Debes invertir con un horizonte de años (3, 5, 10 años), no de días. Si necesitas ese dinero la semana que viene, déjalo en el banco.
        
        #### 🥈 Regla 2: Acepta la Montaña Rusa (La Volatilidad es tu amiga)
        Los precios suben y bajan. No entres en pánico si tu cartera baja un 2% un martes. Las caídas a veces son simples "rebajas" para comprar más barato. Usa el **Monitor de Riesgo Macro (RVM)** de FirstFolio para diferenciar una simple bajada temporal de una crisis estructural.
        
        #### 🥉 Regla 3: Huye del "Hype" y del FOMO (El Ruido Mediático)
        Si un foro de internet te dice que compres una acción con urgencia, probablemente ya llegas tarde. Para protegerte, usa nuestro **Radar de Oportunidades**. Nuestra IA medirá el *Nivel de Hype* (Ley de Amara) de cada noticia antes de que pulses comprar. Invierte por los fundamentos reales, no por la moda de la semana.
        """)

    st.markdown("---")
    st.subheader("🏆 Evaluación Final: Reto de Simulación")
    st.write("Demuestra lo aprendido para desbloquear tu nivel de Inversor Junior:")
    
    q1 = st.radio("1. Has detectado una noticia con un 'Nivel de Hype' extremo (100/100). Según FirstFolio, ¿qué precaución deberías tomar?", 
                  ["a) Comprar inmediatamente usando una Orden a Mercado.", 
                   "b) Evaluar el riesgo, ya que el activo podría estar sobreestimado a corto plazo (Ley de Amara).", 
                   "c) Invertir todo en Cetes o Letras del Tesoro."], index=None)
                   
    q2 = st.radio("2. Quieres comprar acciones de una tecnológica, pero solo estás dispuesto a pagar un precio máximo fijado por ti. ¿Qué orden utilizas?", 
                  ["a) Orden a Mercado.", 
                   "b) Stop-loss.", 
                   "c) Orden Limitada."], index=None)
                   
    q3 = st.radio("3. Es el precio al que los vendedores en el mercado están dispuestos a vender sus acciones:", 
                  ["a) Bid.", 
                   "b) Ask / Offer.", 
                   "c) Spread."], index=None)
                   
    q4 = st.radio("4. ¿Qué herramienta configuras en tu bróker para limitar tus pérdidas si el mercado cae de forma abrupta?", 
                  ["a) Orden Stop-loss.", 
                   "b) Orden a Mercado.", 
                   "c) ETF."], index=None)

    if st.button("✅ Enviar Respuestas", key="btn_quiz"):
        if q1 and q2 and q3 and q4:
            if q1.startswith("b") and q2.startswith("c") and q3.startswith("b") and q4.startswith("a"):
                st.balloons()
                st.success("🎉 **¡Felicidades!** Has respondido correctamente a todas las preguntas. Estás listo para analizar el mercado en el Radar de Oportunidades.")
            else:
                st.error("❌ Algunas respuestas son incorrectas. Revisa las lecciones del Aula Virtual e inténtalo de nuevo.")
        else:
            st.warning("Por favor, responde a todas las preguntas antes de enviar.")
