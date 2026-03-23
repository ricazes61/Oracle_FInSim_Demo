# app.py
# Aplicación principal del Simulador de Performance Financiera Bancaria.
# Framework: Streamlit | Motor: model.py | Datos: utils.py
# Para ejecutar: streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from model import (
    EscenarioInput,
    calcular_resultados,
    proyectar_12_meses,
    construir_puente_roe,
)
from utils import (
    cargar_escenarios,
    cargar_sensibilidades,
    cargar_configuracion,
    fila_a_escenario,
    construir_tabla_comparativa,
    generar_insights,
    exportar_escenario_csv,
    fmt_moneda,
    fmt_pct,
    fmt_variacion,
)

# ---------------------------------------------------------------------------
# Configuración de página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Simulador Financiero Bancario",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS ejecutivo: estilo McKinsey/BCG — limpio, sobrio, profesional
# ---------------------------------------------------------------------------
st.markdown("""
<style>
  /* ---- Variables de color ---- */
  :root {
    --bg: #F7F8FA;
    --card: #FFFFFF;
    --primary: #1B3A6B;
    --secondary: #4B6FA5;
    --accent-green: #0F7B55;
    --accent-red: #C0392B;
    --accent-yellow: #F39C12;
    --text-primary: #1A1D2E;
    --text-secondary: #6B7280;
    --border-color: #E5E7EB;
  }
  
  body {
    background-color: var(--bg);
    color: var(--text-primary);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }
  
  /* ---- HEADER PRINCIPAL ---- */
  .header-title {
    color: var(--primary);
    font-size: 2.2em;
    font-weight: 700;
    letter-spacing: -0.5px;
    margin-bottom: 0.2em;
  }
  
  .header-subtitle {
    color: var(--text-secondary);
    font-size: 1.1em;
    font-weight: 400;
    margin-bottom: 1.5em;
  }
  
  /* ---- TARJETAS KPI ---- */
  .kpi-card {
    background: var(--card);
    padding: 1.5em;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border-left: 4px solid var(--primary);
    margin-bottom: 1em;
  }
  
  .kpi-label {
    color: var(--text-secondary);
    font-size: 0.9em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5em;
  }
  
  .kpi-value {
    color: var(--primary);
    font-size: 1.8em;
    font-weight: 700;
    margin-bottom: 0.3em;
  }
  
  .kpi-variation {
    font-size: 0.85em;
    font-weight: 500;
  }
  
  .kpi-variation.positive {
    color: var(--accent-green);
  }
  
  .kpi-variation.negative {
    color: var(--accent-red);
  }
  
  .kpi-variation.neutral {
    color: var(--text-secondary);
  }
  
  /* ---- PANEL LATERAL ---- */
  .sidebar-section {
    background: var(--card);
    padding: 1.2em;
    border-radius: 8px;
    margin-bottom: 1em;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  }
  
  .sidebar-title {
    color: var(--primary);
    font-size: 1.1em;
    font-weight: 700;
    margin-bottom: 1em;
    border-bottom: 2px solid var(--primary);
    padding-bottom: 0.7em;
  }
  
  .stSlider > label {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
  }
  
  /* ---- TABLA COMPARATIVA ---- */
  .table-container {
    background: var(--card);
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    padding: 1.5em;
  }
  
  table {
    border-collapse: collapse;
    width: 100%;
  }
  
  th {
    background-color: var(--primary);
    color: white;
    padding: 1em;
    text-align: left;
    font-weight: 700;
    border: none;
  }
  
  td {
    padding: 0.8em 1em;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-primary);
  }
  
  tr:hover {
    background-color: #F3F4F6;
  }
  
  /* ---- BOTONES ---- */
  .stButton > button {
    background-color: var(--primary) !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    padding: 0.6em 1.2em !important;
    border: none !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12) !important;
  }
  
  .stButton > button:hover {
    background-color: var(--secondary) !important;
  }
  
  /* ---- ALERTAS E INSIGHTS ---- */
  .insight-card {
    background: var(--card);
    padding: 1em;
    border-radius: 6px;
    border-left: 4px solid var(--primary);
    margin-bottom: 0.8em;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  }
  
  .insight-card.positivo {
    border-left-color: var(--accent-green);
  }
  
  .insight-card.negativo {
    border-left-color: var(--accent-red);
  }
  
  .insight-card.critico {
    border-left-color: var(--accent-red);
    background: #FEF2F2;
  }
  
  .insight-card.atención {
    border-left-color: var(--accent-yellow);
    background: #FFFBEB;
  }
  
  .insight-message {
    color: var(--text-primary);
    font-size: 0.95em;
    font-weight: 500;
  }
  
  /* ---- SECCIÓN TÍTULOS ---- */
  .section-title {
    color: var(--primary);
    font-size: 1.4em;
    font-weight: 700;
    margin-top: 2em;
    margin-bottom: 1em;
    border-bottom: 3px solid var(--primary);
    padding-bottom: 0.5em;
  }
  
  /* ---- DIVIDER CUSTOM ---- */
  .custom-divider {
    border-top: 1px solid var(--border-color);
    margin: 1em 0;
  }
  
  /* ---- RESPONSIVE ---- */
  @media (max-width: 768px) {
    .header-title {
      font-size: 1.8em;
    }
    .kpi-value {
      font-size: 1.4em;
    }
  }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# INICIALIZAR SESSION STATE
# ---------------------------------------------------------------------------
if "escenario_actual" not in st.session_state:
    st.session_state.escenario_actual = None
if "resultado_base" not in st.session_state:
    st.session_state.resultado_base = None
if "resultado_escenario" not in st.session_state:
    st.session_state.resultado_escenario = None


# ---------------------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------------------
@st.cache_data
def _cargar_todos_los_datos():
    """Carga escenarios, sensibilidades y configuración. Retorna tupla con errores."""
    df_escenarios, err_esc = cargar_escenarios()
    sensibilidades, err_sens = cargar_sensibilidades()
    config_ui, err_config = cargar_configuracion()
    return df_escenarios, err_esc, sensibilidades, err_sens, config_ui, err_config


df_escenarios, err_esc, sensibilidades, err_sens, config_ui, err_config = _cargar_todos_los_datos()

# Mostrar advertencias no críticas
for err in [err_sens, err_config]:
    if err:
        st.warning(f"⚠️ {err}")

# Terminar si falta datos críticos
if df_escenarios is None:
    st.sidebar.error(f"❌ Error crítico: {err_esc}")
    st.sidebar.info("Verifique que `data/escenarios.csv` exista en el directorio actual.")
    st.stop()

# Aplicar valores por defecto si faltan sensibilidades o config
if sensibilidades is None:
    sensibilidades = {
        "sensibilidad_tasa_mora": -0.005,
        "sensibilidad_desempleo_mora": 0.025,
        "sensibilidad_inflacion_mora": 0.010,
    }

if config_ui is None:
    config_ui = {
        "titulo_app": "Simulador de Performance Financiera Bancaria",
        "subtitulo_app": "Modelo integrado para analizar rentabilidad, riesgo y crecimiento",
        "moneda": "USD",
        "decimales": "2",
    }

# ---------------------------------------------------------------------------
# HEADERS
# ---------------------------------------------------------------------------
st.markdown(f'<div class="header-title">{config_ui.get("titulo_app", "Simulador")}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="header-subtitle">{config_ui.get("subtitulo_app", "")}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SIDEBAR: SELECCIÓN Y CONTROL DE ESCENARIOS
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">📊 Panel de Simulación</div>', unsafe_allow_html=True)
    
    # Selector de escenario base
    lista_escenarios = df_escenarios["nombre_escenario"].tolist()
    escenario_seleccionado = st.selectbox(
        "Seleccionar escenario base:",
        lista_escenarios,
        index=0
    )
    
    # Cargar escenario base
    fila_base = df_escenarios[df_escenarios["nombre_escenario"] == escenario_seleccionado].iloc[0]
    escenario_base = fila_a_escenario(fila_base)
    st.session_state.escenario_actual = escenario_base
    
    # Calcular resultado base
    st.session_state.resultado_base = calcular_resultados(escenario_base, sensibilidades)
    
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🎛️ Ajustes de Simulación</div>', unsafe_allow_html=True)
    
    # Sliders para simulación
    col1, col2 = st.columns(2)
    
    with col1:
        tasa_act_var = st.slider(
            "Var. Tasa Activa (bps)",
            -500, 500, 0,
            help="Cambio en basis points de la tasa activa"
        )
        costo_fond_var = st.slider(
            "Var. Costo Fondeo (bps)",
            -300, 300, 0,
            help="Cambio en basis points del costo de fondeo"
        )
        crec_cartera = st.slider(
            "Crec. Cartera (%)",
            -20, 50, 10,
            help="Crecimiento esperado de cartera"
        )
        mora_var = st.slider(
            "Var. Mora (%)",
            -3, 5, 0,
            help="Variación en puntos porcentuales de mora"
        )
    
    with col2:
        inflacion_var = st.slider(
            "Inflación (%)",
            0, 20, int(escenario_base.inflacion * 100),
            help="Tasa de inflación esperada"
        )
        desempleo_var = st.slider(
            "Desempleo (%)",
            2, 15, int(escenario_base.desempleo * 100),
            help="Tasa de desempleo esperada"
        )
        fees_var = st.slider(
            "Var. Fees (%)",
            -30, 50, 0,
            help="Variación en ingresos por comisiones"
        )
        costos_op_var = st.slider(
            "Var. Costos Op. (%)",
            -20, 40, 0,
            help="Variación en costos operativos"
        )
    
    # Construir escenario simulado
    escenario_simulado = EscenarioInput(
        nombre_escenario=f"{escenario_base.nombre_escenario} (Simulado)",
        cartera_total=escenario_base.cartera_total * (1 + crec_cartera / 100),
        tasa_activa=escenario_base.tasa_activa + (tasa_act_var / 10000),
        costo_fondeo=escenario_base.costo_fondeo + (costo_fond_var / 10000),
        mora_base=max(0.001, escenario_base.mora_base + (mora_var / 100)),
        lgd=escenario_base.lgd,
        ingresos_comisiones=escenario_base.ingresos_comisiones * (1 + fees_var / 100),
        costos_operativos=escenario_base.costos_operativos * (1 + costos_op_var / 100),
        equity=escenario_base.equity * (1 + crec_cartera / 100 * 0.5),
        activos_totales=escenario_base.activos_totales * (1 + crec_cartera / 100),
        tasa_impuestos=escenario_base.tasa_impuestos,
        inflacion=inflacion_var / 100,
        desempleo=desempleo_var / 100,
        crecimiento_cartera=crec_cartera / 100,
        objetivo_roe=escenario_base.objetivo_roe,
        objetivo_mora=escenario_base.objetivo_mora,
        objetivo_ratio_eficiencia=escenario_base.objetivo_ratio_eficiencia,
    )
    
    # Calcular resultado del escenario
    st.session_state.resultado_escenario = calcular_resultados(escenario_simulado, sensibilidades)
    
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    
    # Botones de control
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Restablecer", use_container_width=True):
            st.session_state.resultado_escenario = st.session_state.resultado_base
            st.rerun()
    
    with col_btn2:
        if st.button("💾 Descargar CSV", use_container_width=True):
            csv_content = exportar_escenario_csv(
                st.session_state.resultado_escenario,
                escenario_simulado.nombre_escenario
            )
            st.download_button(
                label="Descargar",
                data=csv_content,
                file_name=f"escenario_{escenario_simulado.nombre_escenario}.csv",
                mime="text/csv"
            )

# ---------------------------------------------------------------------------
# MAIN CONTENT
# ---------------------------------------------------------------------------

# SECCIÓN 1: RESUMEN EJECUTIVO (KPIs)
st.markdown('<div class="section-title">📈 Resumen Ejecutivo</div>', unsafe_allow_html=True)

resultado_base = st.session_state.resultado_base
resultado_esc = st.session_state.resultado_escenario

cols_kpi = st.columns(3)
kpis_data = [
    ("ROE", fmt_pct(resultado_esc.roe, 1), fmt_variacion(resultado_base.roe, resultado_esc.roe, como_pct=True)),
    ("ROA", fmt_pct(resultado_esc.roa, 2), fmt_variacion(resultado_base.roa, resultado_esc.roa, como_pct=True)),
    ("Utilidad Neta", fmt_moneda(resultado_esc.utilidad_neta), fmt_variacion(resultado_base.utilidad_neta, resultado_esc.utilidad_neta)),
    ("Margen Financiero", fmt_moneda(resultado_esc.margen_financiero), fmt_variacion(resultado_base.margen_financiero, resultado_esc.margen_financiero)),
    ("NIM", fmt_pct(resultado_esc.nim, 2), fmt_variacion(resultado_base.nim, resultado_esc.nim, como_pct=True)),
    ("Costo de Riesgo", fmt_pct(resultado_esc.costo_riesgo, 2), fmt_variacion(resultado_base.costo_riesgo, resultado_esc.costo_riesgo, como_pct=True)),
    ("Provisiones", fmt_moneda(resultado_esc.provisiones), fmt_variacion(resultado_base.provisiones, resultado_esc.provisiones)),
    ("Ratio Eficiencia", fmt_pct(resultado_esc.ratio_eficiencia, 1), fmt_variacion(resultado_base.ratio_eficiencia, resultado_esc.ratio_eficiencia, como_pct=True)),
    ("Cartera Total", fmt_moneda(resultado_esc.cartera_total), fmt_variacion(resultado_base.cartera_total, resultado_esc.cartera_total)),
]

for idx, (label, valor, variacion) in enumerate(kpis_data):
    col_idx = idx % 3
    
    # Determinar color de variación
    try:
        var_num = float(variacion.replace("%", "").replace("+", "").replace("$", "").split()[0]) if variacion != "N/A" else 0
        var_clase = "positive" if var_num > 0 else ("negative" if var_num < 0 else "neutral")
    except:
        var_clase = "neutral"
    
    cards_html = f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{valor}</div>
        <div class="kpi-variation {var_clase}">{variacion}</div>
    </div>
    """
    cols_kpi[col_idx].markdown(cards_html, unsafe_allow_html=True)

# SECCIÓN 2: IMPACTO FINANCIERO
st.markdown('<div class="section-title">💰 Impacto Financiero</div>', unsafe_allow_html=True)

tabla_comparativa = construir_tabla_comparativa(resultado_base, resultado_esc, config_ui)

# Formatear tabla para display
tabla_display = tabla_comparativa.copy()
for col in ["Base", "Escenario", "Variación $"]:
    if col in tabla_display.columns:
        tabla_display[col] = tabla_display[col].apply(lambda x: fmt_moneda(x))
tabla_display["Variación %"] = tabla_display["Variación %"].apply(lambda x: f"{x:.2f}%")

st.dataframe(tabla_display, use_container_width=True, hide_index=True)

# SECCIÓN 3: ALERTAS E INSIGHTS
st.markdown('<div class="section-title">⚡ Alertas e Insights</div>', unsafe_allow_html=True)

col_insights, col_status = st.columns([2, 1])

with col_insights:
    insights = generar_insights(resultado_base, resultado_esc, config_ui)
    for insight in insights:
        insight_html = f"""
        <div class="insight-card {insight['tipo']}">
            <div class="insight-message">{insight['mensaje']}</div>
        </div>
        """
        st.markdown(insight_html, unsafe_allow_html=True)

with col_status:
    st.subheader("Estado General")
    
    # Semáforo simple
    mora_critica = float(config_ui.get("mora_critica", "0.06"))
    roe_objetivo = float(config_ui.get("roe_objetivo_default", "0.15"))
    roe_critico = float(config_ui.get("umbral_roe_critico", "0.08"))
    
    if resultado_esc.mora_ajustada > mora_critica or resultado_esc.roe < roe_critico:
        estado = "🔴 Crítico"
        color = "red"
    elif resultado_esc.mora_ajustada > float(config_ui.get("mora_atencion", "0.045")) or resultado_esc.roe < roe_objetivo:
        estado = "🟡 Atención"
        color = "orange"
    else:
        estado = "🟢 Saludable"
        color = "green"
    
    st.markdown(f"<h2 style='color: {color}; text-align: center;'>{estado}</h2>", unsafe_allow_html=True)

# SECCIÓN 4: GRÁFICOS
st.markdown('<div class="section-title">📊 Análisis Comparativo</div>', unsafe_allow_html=True)

col_g1, col_g2 = st.columns(2)

# Gráfico 1: Comparación Base vs Escenario
with col_g1:
    fig_comp = go.Figure()
    
    indicadores_plot = ["Utilidad Neta", "ROE", "NIM", "Ratio Eficiencia"]
    valores_base = [
        resultado_base.utilidad_neta / 1e9,
        resultado_base.roe * 100,
        resultado_base.nim * 100,
        resultado_base.ratio_eficiencia * 100,
    ]
    valores_esc = [
        resultado_esc.utilidad_neta / 1e9,
        resultado_esc.roe * 100,
        resultado_esc.nim * 100,
        resultado_esc.ratio_eficiencia * 100,
    ]
    
    fig_comp.add_trace(go.Bar(
        x=indicadores_plot,
        y=valores_base,
        name="Base",
        marker_color="#1B3A6B",
        text=[f"{v:.2f}" for v in valores_base],
        textposition="auto",
    ))
    
    fig_comp.add_trace(go.Bar(
        x=indicadores_plot,
        y=valores_esc,
        name="Escenario",
        marker_color="#0F7B55",
        text=[f"{v:.2f}" for v in valores_esc],
        textposition="auto",
    ))
    
    fig_comp.update_layout(
        title="Comparación Base vs Escenario",
        xaxis_title="Indicador",
        yaxis_title="Valor",
        barmode="group",
        template="plotly_white",
        height=400,
        font=dict(size=11),
    )
    
    st.plotly_chart(fig_comp, use_container_width=True)

# Gráfico 2: Puente de ROE
with col_g2:
    puente = construir_puente_roe(resultado_base, resultado_esc)
    
    fig_puente = go.Figure()
    
    fig_puente.add_trace(go.Waterfall(
        x=["ROE Base", "Cambio Utilidad", "Cambio Equity", "ROE Escenario"],
        y=[puente["roe_base"] * 100, puente["cambio_utilidad_neta"] * 100, puente["cambio_equity"] * 100, puente["roe_escenario"] * 100],
        connector={"line": {"color": "#1B3A6B"}},
        increasing={"marker": {"color": "#0F7B55"}},
        decreasing={"marker": {"color": "#C0392B"}},
        text=[f"{v:.2f}%" for v in [puente["roe_base"] * 100, puente["cambio_utilidad_neta"] * 100, puente["cambio_equity"] * 100, puente["roe_escenario"] * 100]],
        textposition="auto",
        totals={"marker": {"color": "#4B6FA5"}},
    ))
    
    fig_puente.update_layout(
        title="Puente de ROE",
        yaxis_title="ROE (%)",
        template="plotly_white",
        height=400,
        font=dict(size=11),
        showlegend=False,
    )
    
    st.plotly_chart(fig_puente, use_container_width=True)

# Gráfico 3: Proyección 12 meses
st.markdown('<div class="section-title">📈 Proyección Simplificada 12 Meses</div>', unsafe_allow_html=True)

meses = list(range(1, 13))
proyecciones = proyectar_12_meses(resultado_esc, factor_crecimiento=1.02)

roe_proyectado = [p.roe * 100 for p in proyecciones]
utilidad_proyectada = [p.utilidad_neta / 1e9 for p in proyecciones]

fig_proj = make_subplots(
    rows=1, cols=2,
    subplot_titles=("ROE Proyectado", "Utilidad Neta Proyectada"),
    specs=[[{"secondary_y": False}, {"secondary_y": False}]]
)

fig_proj.add_trace(
    go.Scatter(
        x=meses,
        y=roe_proyectado,
        mode="lines+markers",
        name="ROE",
        line=dict(color="#1B3A6B", width=3),
        marker=dict(size=8),
    ),
    row=1, col=1
)

fig_proj.add_trace(
    go.Scatter(
        x=meses,
        y=utilidad_proyectada,
        mode="lines+markers",
        name="Utilidad Neta",
        line=dict(color="#0F7B55", width=3),
        marker=dict(size=8),
    ),
    row=1, col=2
)

fig_proj.update_xaxes(title_text="Mes", row=1, col=1)
fig_proj.update_xaxes(title_text="Mes", row=1, col=2)
fig_proj.update_yaxes(title_text="ROE (%)", row=1, col=1)
fig_proj.update_yaxes(title_text="Utilidad (B USD)", row=1, col=2)

fig_proj.update_layout(
    title_text="Proyección Simplificada 12 Meses",
    template="plotly_white",
    height=400,
    font=dict(size=11),
)

st.plotly_chart(fig_proj, use_container_width=True)

# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------
st.markdown("""
---
<div style='text-align: center; color: #6B7280; font-size: 0.85em; padding: 2em 0;'>
    <strong>Oracle FIn Sim Demo</strong> | Simulador de Performance Financiera Bancaria<br>
    Versión 1.0 | Modelo simple para demos comerciales
</div>
""", unsafe_allow_html=True)
