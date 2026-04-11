
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scipy.stats import linregress

# --- CONFIGURACIÓN ---
ACTIVOS = {
    'LatAm': {
        'BRL=X': {'Pais': 'Brasil', 'ISO': 'BRA', 'Directo': True},
        'MXN=X': {'Pais': 'México', 'ISO': 'MEX', 'Directo': True},
        'COP=X': {'Pais': 'Colombia', 'ISO': 'COL', 'Directo': True},
        'CLP=X': {'Pais': 'Chile', 'ISO': 'CHL', 'Directo': True},
        'PEN=X': {'Pais': 'Perú', 'ISO': 'PER', 'Directo': True}
    },
    'Asia': {
        'JPY=X': {'Pais': 'Japón', 'ISO': 'JPN', 'Directo': True},
        'CNY=X': {'Pais': 'China', 'ISO': 'CHN', 'Directo': True},
        'INR=X': {'Pais': 'India', 'ISO': 'IND', 'Directo': True},
        'KRW=X': {'Pais': 'Corea', 'ISO': 'KOR', 'Directo': True}
    },
    'G10 (Ref)': {
        'EURUSD=X': {'Pais': 'Eurozona', 'ISO': 'EUR', 'Directo': False},
        'GBPUSD=X': {'Pais': 'Reino Unido', 'ISO': 'GBR', 'Directo': False}
    }
}

class RVMAnalytics:
    def __init__(self):
        self.umbrales = {'vol_asim_critica': 12.0, 'deval_critica': 20.0}

    # Usamos caché de Streamlit para no descargar datos repetidamente
    @st.cache_data(ttl=3600) 
    def obtener_datos(_self): # El _self es un truco de streamlit para ignorar el objeto en el hash
        FECHA_FIN = datetime.now()
        FECHA_INICIO = FECHA_FIN - timedelta(days=730)
        resultados = []
        
        for region, tickers in ACTIVOS.items():
            for ticker, info in tickers.items():
                try:
                    df = yf.download(ticker, start=FECHA_INICIO, end=FECHA_FIN, progress=False)
                    if df.empty or len(df) < 200: continue
                    df = df.dropna()

                    # 1. Retornos
                    df['Log_Ret'] = np.log(df['Close'] / df['Close'].shift(1))
                    
                    # 2. Orientación
                    if info['Directo']:
                        retornos_malos = df[df['Log_Ret'] > 0]['Log_Ret']
                        precio_ini = df['Close'].iloc[-252].item()
                        precio_fin = df['Close'].iloc[-1].item()
                        devaluacion = ((precio_fin - precio_ini) / precio_ini) * 100
                        slope_factor = 1 # Pendiente positiva = Riesgo
                    else:
                        retornos_malos = df[df['Log_Ret'] < 0]['Log_Ret']
                        precio_ini = df['Close'].iloc[-252].item()
                        precio_fin = df['Close'].iloc[-1].item()
                        devaluacion = ((precio_ini - precio_fin) / precio_ini) * 100
                        slope_factor = -1 # Pendiente negativa = Riesgo

                    # 3. Métricas
                    vol_asim = retornos_malos.std() * np.sqrt(252) * 100 if not retornos_malos.empty else 0
                    vol_total = df['Log_Ret'].std() * np.sqrt(252) * 100
                    
                    # 4. Tendencia (R2)
                    reciente = df['Close'].tail(30).values
                    slope, _, r_value, _, _ = linregress(np.arange(len(reciente)), reciente.flatten())
                    
                    # Ajuste de dirección según el tipo de par
                    slope_ajustada = slope * slope_factor
                    tendencia = "↗️ Acelerando" if slope_ajustada > 0 else "↘️ Relajando"
                    
                    # 5. Histórico (Z-Score)
                    hist_vol = df['Log_Ret'].rolling(30).std() * np.sqrt(252) * 100
                    z_score = (vol_total - hist_vol.mean()) / hist_vol.std() if hist_vol.std() > 0 else 0

                    resultados.append({
                        'Region': region, 'Pais': info['Pais'], 'ISO': info['ISO'],
                        'Vol_Asim': vol_asim, 'Vol_Total': vol_total,
                        'Devaluacion': devaluacion, 'Tendencia': tendencia,
                        'R2': r_value**2, 'Z_Score': z_score
                    })
                except Exception: continue

        return pd.DataFrame(resultados)

    def calcular_iv_score(self, df):
        # Normalización
        abs_asim = (df['Vol_Asim'] / self.umbrales['vol_asim_critica']).clip(0, 1) * 100
        abs_deval = (df['Devaluacion'].clip(lower=0) / self.umbrales['deval_critica']).clip(0, 1) * 100
        rel_asim = df['Vol_Asim'].rank(pct=True) * 100
        hist_score = (1 / (1 + np.exp(-df['Z_Score']))) * 100
        
        # IV Score (Fórmula Triple)
        score_asim_final = (0.6 * abs_asim) + (0.2 * rel_asim) + (0.2 * hist_score)
        
        df['IV_Score'] = (0.5 * score_asim_final) + \
                         (0.3 * (df['Vol_Total']/15).clip(0,1)*100) + \
                         (0.2 * abs_deval)
        df['IV_Score'] = df['IV_Score'].round(1)
        
        conditions = [df['IV_Score'] > 60, df['IV_Score'] > 40]
        df['Senal'] = np.select(conditions, ['🔴 CRÍTICO', '⚠️ ALERTA'], default='🟢 ESTABLE')
        return df

    def generar_graficos(self, df):
        layout = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        
        # Mapa
        fig_map = px.choropleth(df, locations="ISO", color="IV_Score",
                                color_continuous_scale="RdYlGn_r", range_color=[0, 100],
                                hover_name="Pais", title="<b>MAPA DE CALOR (Riesgo Estructural)</b>")
        fig_map.update_layout(margin=dict(l=0,r=0,t=30,b=0), geo=dict(bgcolor='rgba(0,0,0,0)', showland=True, landcolor='#222'), **layout)

        # Radar
        fig_radar = go.Figure()
        colores = {'LatAm': '#FF5733', 'Asia': '#33C1FF', 'G10 (Ref)': '#AAAAAA'}
        for reg in df['Region'].unique():
            dfr = df[df['Region'] == reg]
            r = list(dfr['IV_Score']) + [dfr['IV_Score'].iloc[0]]
            t = list(dfr['Pais']) + [dfr['Pais'].iloc[0]]
            fig_radar.add_trace(go.Scatterpolar(r=r, theta=t, fill='toself', name=reg, line_color=colores.get(reg, 'white')))
        fig_radar.update_layout(polar=dict(bgcolor="#111", radialaxis=dict(range=[0, 100])), **layout)

        return fig_map, fig_radar

# Instancia global para usar en app.py
analitics = RVMAnalytics()
