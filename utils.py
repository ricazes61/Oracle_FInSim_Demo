# utils.py
# Funciones auxiliares: carga de datos, validación, formateo, insights y exportación.
# Diseñado para ser importado desde app.py sin acoplamiento con la UI.

import pandas as pd
import numpy as np
import io
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from model import EscenarioInput, ResultadoFinanciero


# ---------------------------------------------------------------------------
# Rutas base (relativas al directorio donde se ejecuta app.py)
# ---------------------------------------------------------------------------
DATA_DIR = Path("data")
PATH_ESCENARIOS = DATA_DIR / "escenarios.csv"
PATH_SENSIBILIDADES = DATA_DIR / "sensibilidades.csv"
PATH_CONFIGURACION = DATA_DIR / "configuracion_ui.csv"


# ---------------------------------------------------------------------------
# Columnas mínimas requeridas por CSV
# ---------------------------------------------------------------------------
COLUMNAS_ESCENARIOS = [
    "nombre_escenario", "cartera_total", "tasa_activa", "costo_fondeo",
    "mora_base", "lgd", "ingresos_comisiones", "costos_operativos",
    "equity", "activos_totales", "tasa_impuestos", "inflacion",
    "desempleo", "crecimiento_cartera", "objetivo_roe",
    "objetivo_mora", "objetivo_ratio_eficiencia"
]
COLUMNAS_SENSIBILIDADES = ["parametro", "valor"]
COLUMNAS_CONFIGURACION = ["clave", "valor"]


# ---------------------------------------------------------------------------
# Carga de archivos CSV con validación básica
# ---------------------------------------------------------------------------

def cargar_escenarios() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Carga el archivo de escenarios.
    Retorna (DataFrame, None) si éxito, o (None, mensaje_error) si falla.
    """
    try:
        df = pd.read_csv(PATH_ESCENARIOS)
        columnas_faltantes = [c for c in COLUMNAS_ESCENARIOS if c not in df.columns]
        if columnas_faltantes:
            return None, f"Columnas faltantes en escenarios.csv: {', '.join(columnas_faltantes)}"
        # Convertir columnas numéricas
        for col in COLUMNAS_ESCENARIOS[1:]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[COLUMNAS_ESCENARIOS[1:]].isnull().any().any():
            return None, "Hay valores no numéricos en escenarios.csv. Revise el archivo."
        return df, None
    except FileNotFoundError:
        return None, f"Archivo no encontrado: {PATH_ESCENARIOS}"
    except Exception as e:
        return None, f"Error al leer escenarios.csv: {str(e)}"


def cargar_sensibilidades() -> Tuple[Optional[Dict[str, float]], Optional[str]]:
    """
    Carga el archivo de sensibilidades.
    Retorna (Dict, None) si éxito, o (None, mensaje_error) si falla.
    """
    try:
        df = pd.read_csv(PATH_SENSIBILIDADES)
        if "parametro" not in df.columns or "valor" not in df.columns:
            return None, "Sensibilidades.csv debe tener columnas 'parametro' y 'valor'"
        sensibilidades = dict(zip(df["parametro"], pd.to_numeric(df["valor"], errors="coerce")))
        return sensibilidades, None
    except FileNotFoundError:
        return None, f"Archivo no encontrado: {PATH_SENSIBILIDADES}"
    except Exception as e:
        return None, f"Error al leer sensibilidades.csv: {str(e)}"


def cargar_configuracion() -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    """
    Carga el archivo de configuración UI.
    Retorna (Dict, None) si éxito, o (None, mensaje_error) si falla.
    """
    try:
        df = pd.read_csv(PATH_CONFIGURACION)
        if "clave" not in df.columns or "valor" not in df.columns:
            return None, "Configuracion_ui.csv debe tener columnas 'clave' y 'valor'"
        config = dict(zip(df["clave"].astype(str).str.strip(), df["valor"].astype(str).str.strip()))
        return config, None
    except FileNotFoundError:
        return None, f"Archivo no encontrado: {PATH_CONFIGURACION}"
    except Exception as e:
        return None, f"Error al leer configuracion_ui.csv: {str(e)}"


# ---------------------------------------------------------------------------
# Conversión de filas a objetos de entrada
# ---------------------------------------------------------------------------

def fila_a_escenario(row: pd.Series) -> EscenarioInput:
    """Convierte una fila de DataFrame a EscenarioInput."""
    return EscenarioInput(
        nombre_escenario=str(row["nombre_escenario"]),
        cartera_total=float(row["cartera_total"]),
        tasa_activa=float(row["tasa_activa"]),
        costo_fondeo=float(row["costo_fondeo"]),
        mora_base=float(row["mora_base"]),
        lgd=float(row["lgd"]),
        ingresos_comisiones=float(row["ingresos_comisiones"]),
        costos_operativos=float(row["costos_operativos"]),
        equity=float(row["equity"]),
        activos_totales=float(row["activos_totales"]),
        tasa_impuestos=float(row["tasa_impuestos"]),
        inflacion=float(row["inflacion"]),
        desempleo=float(row["desempleo"]),
        crecimiento_cartera=float(row["crecimiento_cartera"]),
        objetivo_roe=float(row["objetivo_roe"]),
        objetivo_mora=float(row["objetivo_mora"]),
        objetivo_ratio_eficiencia=float(row["objetivo_ratio_eficiencia"]),
    )


# ---------------------------------------------------------------------------
# Construcción de tablas comparativas
# ---------------------------------------------------------------------------

def construir_tabla_comparativa(
    resultado_base: ResultadoFinanciero,
    resultado_escenario: ResultadoFinanciero,
    config_ui: Dict[str, str]
) -> pd.DataFrame:
    """
    Construye una tabla comparativa entre escenario base y escenario actual.
    """
    decimales = int(config_ui.get("decimales", "2"))
    
    indicadores = [
        ("Ingresos por Intereses", resultado_base.ingresos_intereses, resultado_escenario.ingresos_intereses),
        ("Ingresos por Comisiones", resultado_base.ingresos_comisiones, resultado_escenario.ingresos_comisiones),
        ("Margen Financiero", resultado_base.margen_financiero, resultado_escenario.margen_financiero),
        ("Costo de Fondeo", resultado_base.costos_fondeo, resultado_escenario.costos_fondeo),
        ("Costo de Riesgo", resultado_base.costo_riesgo, resultado_escenario.costo_riesgo),
        ("Provisiones", resultado_base.provisiones, resultado_escenario.provisiones),
        ("Costos Operativos", resultado_base.costos_operativos, resultado_escenario.costos_operativos),
        ("Resultado Antes de Impuestos", resultado_base.resultado_antes_impuestos, resultado_escenario.resultado_antes_impuestos),
        ("Utilidad Neta", resultado_base.utilidad_neta, resultado_escenario.utilidad_neta),
        ("ROE", resultado_base.roe, resultado_escenario.roe),
        ("ROA", resultado_base.roa, resultado_escenario.roa),
        ("NIM", resultado_base.nim, resultado_escenario.nim),
        ("Ratio de Eficiencia", resultado_base.ratio_eficiencia, resultado_escenario.ratio_eficiencia),
    ]
    
    filas = []
    for nombre, base, escenario in indicadores:
        delta_abs = escenario - base
        delta_pct = (delta_abs / base * 100) if base != 0 else 0
        
        filas.append({
            "Indicador": nombre,
            "Base": base,
            "Escenario": escenario,
            "Variación $": delta_abs,
            "Variación %": delta_pct,
        })
    
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------
# Generación de insights automáticos
# ---------------------------------------------------------------------------

def generar_insights(
    resultado_base: ResultadoFinanciero,
    resultado_escenario: ResultadoFinanciero,
    config_ui: Dict[str, str]
) -> List[Dict[str, str]]:
    """
    Genera insights automáticos comparando escenario base vs actual.
    """
    insights = []
    
    # Umbrales de configuración
    mora_critica = float(config_ui.get("mora_critica", "0.06"))
    mora_atencion = float(config_ui.get("mora_atencion", "0.045"))
    roe_objetivo = float(config_ui.get("roe_objetivo_default", "0.15"))
    roe_critico = float(config_ui.get("umbral_roe_critico", "0.08"))
    ratio_efic_objetivo = float(config_ui.get("ratio_eficiencia_objetivo", "0.50"))
    
    # 1. Alerta de mora
    if resultado_escenario.mora_ajustada > mora_critica:
        insights.append({
            "tipo": "crítico",
            "mensaje": f"⚠️ Mora proyectada ({resultado_escenario.mora_ajustada:.1%}) supera el umbral crítico ({mora_critica:.1%})."
        })
    elif resultado_escenario.mora_ajustada > mora_atencion:
        insights.append({
            "tipo": "atención",
            "mensaje": f"⚠️ Mora proyectada ({resultado_escenario.mora_ajustada:.1%}) requiere atención."
        })
    
    # 2. Impacto de tasas en margen
    delta_margen = resultado_escenario.margen_financiero - resultado_base.margen_financiero
    delta_mora = resultado_escenario.mora_ajustada - resultado_base.mora_ajustada
    if delta_margen > 0 and delta_mora > 0:
        insights.append({
            "tipo": "neutral",
            "mensaje": "📊 Aumento de tasas mejora margen, pero incrementa mora."
        })
    
    # 3. Alerta de ROE
    if resultado_escenario.roe < roe_critico:
        insights.append({
            "tipo": "crítico",
            "mensaje": f"🔴 ROE ({resultado_escenario.roe:.1%}) cae bajo el mínimo crítico ({roe_critico:.1%})."
        })
    elif resultado_escenario.roe < roe_objetivo:
        insights.append({
            "tipo": "atención",
            "mensaje": f"🟡 ROE ({resultado_escenario.roe:.1%}) por debajo del objetivo ({roe_objetivo:.1%})."
        })
    else:
        insights.append({
            "tipo": "positivo",
            "mensaje": f"🟢 ROE ({resultado_escenario.roe:.1%}) en línea con objetivo."
        })
    
    # 4. Presión en eficiencia
    if resultado_escenario.ratio_eficiencia > ratio_efic_objetivo:
        insights.append({
            "tipo": "atención",
            "mensaje": f"📈 Ratio de eficiencia ({resultado_escenario.ratio_eficiencia:.1%}) superior al objetivo ({ratio_efic_objetivo:.1%})."
        })
    
    # 5. Provisiones vs cartera
    prov_ratio_base = resultado_base.provisiones / resultado_base.cartera_total
    prov_ratio_esc = resultado_escenario.provisiones / resultado_escenario.cartera_total
    if prov_ratio_esc > prov_ratio_base * 1.2:
        insights.append({
            "tipo": "atención",
            "mensaje": "📉 Crecimiento de provisiones ejerce presión sobre utilidad."
        })
    
    # 6. Crecimiento positivo de utilidad
    delta_util = resultado_escenario.utilidad_neta - resultado_base.utilidad_neta
    if delta_util > 0:
        pct_util = (delta_util / resultado_base.utilidad_neta * 100) if resultado_base.utilidad_neta > 0 else 0
        insights.append({
            "tipo": "positivo",
            "mensaje": f"💰 Utilidad neta creció {pct_util:.1f}% en el escenario."
        })
    elif delta_util < 0:
        pct_util = (delta_util / resultado_base.utilidad_neta * 100) if resultado_base.utilidad_neta > 0 else 0
        insights.append({
            "tipo": "negativo",
            "mensaje": f"⚠️ Utilidad neta cayó {abs(pct_util):.1f}% en el escenario."
        })
    
    return insights if insights else [{"tipo": "neutral", "mensaje": "Sin cambios relevantes."}]


# ---------------------------------------------------------------------------
# Funciones de formateo
# ---------------------------------------------------------------------------

def fmt_moneda(valor: float, decimales: int = 2, abr: str = "") -> str:
    """Formatea un número como moneda."""
    if abs(valor) >= 1_000_000_000:
        return f"${valor / 1_000_000_000:.{decimales}f}B {abr}".strip()
    elif abs(valor) >= 1_000_000:
        return f"${valor / 1_000_000:.{decimales}f}M {abr}".strip()
    elif abs(valor) >= 1_000:
        return f"${valor / 1_000:.{decimales}f}K {abr}".strip()
    else:
        return f"${valor:.{decimales}f} {abr}".strip()


def fmt_pct(valor: float, decimales: int = 1) -> str:
    """Formatea un número como porcentaje."""
    return f"{valor * 100:.{decimales}f}%"


def fmt_variacion(valor_base: float, valor_nuevo: float, como_pct: bool = False) -> str:
    """
    Formatea la variación entre dos valores.
    Retorna string tipo "+1.5M (2.3%)" o "+2.3%"
    """
    if valor_base == 0:
        return "N/A"
    
    delta = valor_nuevo - valor_base
    pct = (delta / valor_base * 100) if valor_base != 0 else 0
    
    if como_pct:
        signo = "+" if delta >= 0 else ""
        return f"{signo}{pct:.1f}%"
    else:
        signo = "+" if delta >= 0 else ""
        return f"{signo}{fmt_moneda(delta)} ({signo}{pct:.1f}%)"


# ---------------------------------------------------------------------------
# Exportación
# ---------------------------------------------------------------------------

def exportar_escenario_csv(
    resultado: ResultadoFinanciero,
    nombre_escenario: str
) -> str:
    """
    Exporta un escenario completo a formato CSV.
    Retorna el contenido como string.
    """
    datos = {
        "Métrica": [
            "Ingresos por Intereses",
            "Costos de Fondeo",
            "Margen Financiero",
            "Ingresos por Comisiones",
            "Mora Ajustada",
            "Provisiones",
            "Costo de Riesgo",
            "Ingreso Total",
            "Costos Operativos",
            "Resultado Antes de Impuestos",
            "Utilidad Neta",
            "ROE",
            "ROA",
            "NIM",
            "Ratio de Eficiencia",
        ],
        "Valor": [
            resultado.ingresos_intereses,
            resultado.costos_fondeo,
            resultado.margen_financiero,
            resultado.ingresos_comisiones,
            resultado.mora_ajustada,
            resultado.provisiones,
            resultado.costo_riesgo,
            resultado.ingreso_total,
            resultado.costos_operativos,
            resultado.resultado_antes_impuestos,
            resultado.utilidad_neta,
            resultado.roe,
            resultado.roa,
            resultado.nim,
            resultado.ratio_eficiencia,
        ]
    }
    
    df = pd.DataFrame(datos)
    return df.to_csv(index=False)
