# model.py
# Motor de cálculos financieros para el Simulador.
# Implementa el modelo financiero simplificado con sensibilidades macro.

from dataclasses import dataclass
from typing import Dict, List
import numpy as np


@dataclass
class EscenarioInput:
    """Datos de entrada para un escenario de simulación."""
    nombre_escenario: str
    cartera_total: float
    tasa_activa: float
    costo_fondeo: float
    mora_base: float
    lgd: float
    ingresos_comisiones: float
    costos_operativos: float
    equity: float
    activos_totales: float
    tasa_impuestos: float
    inflacion: float
    desempleo: float
    crecimiento_cartera: float
    objetivo_roe: float
    objetivo_mora: float
    objetivo_ratio_eficiencia: float


@dataclass
class ResultadoFinanciero:
    """Resultado de cálculos financieros."""
    # Ingresos
    ingresos_intereses: float
    costos_fondeo: float
    margen_financiero: float
    ingresos_comisiones: float
    
    # Riesgos y provisiones
    mora_ajustada: float
    provisiones: float
    costo_riesgo: float
    
    # Resultados
    ingreso_total: float
    costos_operativos: float
    resultado_antes_impuestos: float
    utilidad_neta: float
    
    # Ratios
    roe: float
    roa: float
    nim: float
    ratio_eficiencia: float
    
    # Adicionales
    cartera_total: float
    tasa_activa: float
    costo_fondeo: float


def calcular_resultados(
    input_escenario: EscenarioInput,
    sensibilidades: Dict[str, float]
) -> ResultadoFinanciero:
    """
    Calcula los resultados financieros para un escenario.
    
    Args:
        input_escenario: EscenarioInput con parámetros
        sensibilidades: dict con coeficientes de sensibilidad macro
    
    Returns:
        ResultadoFinanciero con todos los KPIs calculados
    """
    
    # =========================================================================
    # 1. CÁLCULO DE MORA AJUSTADA (sensibilidades macro)
    # =========================================================================
    mora_ajustada = input_escenario.mora_base
    mora_ajustada += sensibilidades.get("sensibilidad_tasa_mora", -0.005) * (input_escenario.tasa_activa - 0.18)
    mora_ajustada += sensibilidades.get("sensibilidad_desempleo_mora", 0.025) * (input_escenario.desempleo - 0.08)
    mora_ajustada += sensibilidades.get("sensibilidad_inflacion_mora", 0.010) * (input_escenario.inflacion - 0.06)
    
    # Limitar mora entre 0 y 0.20 (razonable para demo)
    mora_ajustada = max(0.001, min(0.20, mora_ajustada))
    
    # =========================================================================
    # 2. INGRESOS POR INTERESES Y MARGEN FINANCIERO
    # =========================================================================
    ingresos_intereses = input_escenario.cartera_total * input_escenario.tasa_activa
    costos_fondeo = input_escenario.cartera_total * input_escenario.costo_fondeo
    margen_financiero = ingresos_intereses - costos_fondeo
    
    # =========================================================================
    # 3. PROVISIONES Y COSTO DE RIESGO
    # =========================================================================
    provisiones = input_escenario.cartera_total * mora_ajustada * input_escenario.lgd
    costo_riesgo = provisiones / input_escenario.cartera_total if input_escenario.cartera_total > 0 else 0
    
    # =========================================================================
    # 4. RESULTADO OPERATIVO
    # =========================================================================
    ingreso_total = margen_financiero + input_escenario.ingresos_comisiones
    resultado_antes_impuestos = ingreso_total - provisiones - input_escenario.costos_operativos
    
    # =========================================================================
    # 5. UTILIDAD NETA
    # =========================================================================
    utilidad_neta = resultado_antes_impuestos * (1 - input_escenario.tasa_impuestos)
    
    # =========================================================================
    # 6. RATIOS FINANCIEROS
    # =========================================================================
    roe = utilidad_neta / input_escenario.equity if input_escenario.equity > 0 else 0
    roa = utilidad_neta / input_escenario.activos_totales if input_escenario.activos_totales > 0 else 0
    nim = margen_financiero / input_escenario.activos_totales if input_escenario.activos_totales > 0 else 0
    ratio_eficiencia = input_escenario.costos_operativos / ingreso_total if ingreso_total > 0 else 0
    
    return ResultadoFinanciero(
        ingresos_intereses=ingresos_intereses,
        costos_fondeo=costos_fondeo,
        margen_financiero=margen_financiero,
        ingresos_comisiones=input_escenario.ingresos_comisiones,
        mora_ajustada=mora_ajustada,
        provisiones=provisiones,
        costo_riesgo=costo_riesgo,
        ingreso_total=ingreso_total,
        costos_operativos=input_escenario.costos_operativos,
        resultado_antes_impuestos=resultado_antes_impuestos,
        utilidad_neta=utilidad_neta,
        roe=roe,
        roa=roa,
        nim=nim,
        ratio_eficiencia=ratio_eficiencia,
        cartera_total=input_escenario.cartera_total,
        tasa_activa=input_escenario.tasa_activa,
        costo_fondeo=input_escenario.costo_fondeo,
    )


def proyectar_12_meses(
    resultado_base: ResultadoFinanciero,
    factor_crecimiento: float = 1.02
) -> List[ResultadoFinanciero]:
    """
    Proyecta resultados mensuales para los próximos 12 meses.
    Proyección simple: aplica factor de crecimiento mes a mes.
    
    Args:
        resultado_base: Resultado del mes actual
        factor_crecimiento: Factor mensual (ej: 1.02 = 2% mensual)
    
    Returns:
        Lista de 12 ResultadoFinanciero proyectados
    """
    proyecciones = []
    
    for mes in range(1, 13):
        # Aplicar crecimiento acumulado
        factor_acumulado = factor_crecimiento ** mes
        
        # Proyectar componentes principales
        utilidad_proyectada = resultado_base.utilidad_neta * factor_acumulado
        roe_proyectado = resultado_base.roe * factor_acumulado
        
        # Crear resultado proyectado
        resultado_proyectado = ResultadoFinanciero(
            ingresos_intereses=resultado_base.ingresos_intereses * factor_acumulado,
            costos_fondeo=resultado_base.costos_fondeo * factor_acumulado,
            margen_financiero=resultado_base.margen_financiero * factor_acumulado,
            ingresos_comisiones=resultado_base.ingresos_comisiones * factor_acumulado,
            mora_ajustada=resultado_base.mora_ajustada,
            provisiones=resultado_base.provisiones * factor_acumulado,
            costo_riesgo=resultado_base.costo_riesgo,
            ingreso_total=resultado_base.ingreso_total * factor_acumulado,
            costos_operativos=resultado_base.costos_operativos * factor_acumulado,
            resultado_antes_impuestos=resultado_base.resultado_antes_impuestos * factor_acumulado,
            utilidad_neta=utilidad_proyectada,
            roe=roe_proyectado,
            roa=resultado_base.roa * factor_acumulado,
            nim=resultado_base.nim,
            ratio_eficiencia=resultado_base.ratio_eficiencia,
            cartera_total=resultado_base.cartera_total * factor_acumulado,
            tasa_activa=resultado_base.tasa_activa,
            costo_fondeo=resultado_base.costo_fondeo,
        )
        proyecciones.append(resultado_proyectado)
    
    return proyecciones


def construir_puente_roe(
    resultado_base: ResultadoFinanciero,
    resultado_escenario: ResultadoFinanciero
) -> Dict[str, float]:
    """
    Construye un puente (waterfall) que descompone el cambio de ROE.
    
    Args:
        resultado_base: Resultado base
        resultado_escenario: Resultado del escenario actual
    
    Returns:
        Dict con drivers del cambio de ROE
    """
    
    # Cambios absolutos
    delta_utilidad_neta = resultado_escenario.utilidad_neta - resultado_base.utilidad_neta
    delta_equity = (resultado_escenario.cartera_total * 0.15) - (resultado_base.cartera_total * 0.15)
    
    # ROE = Utilidad / Equity
    # Descomposición simplificada:
    # - Cambio por utilidad neta
    # - Cambio por equity
    
    roe_del_cambio_utilidad = delta_utilidad_neta / resultado_base.cartera_total if resultado_base.cartera_total > 0 else 0
    roe_del_cambio_equity = -delta_equity / (resultado_base.cartera_total ** 2) if resultado_base.cartera_total > 0 else 0
    
    return {
        "roe_base": resultado_base.roe,
        "cambio_utilidad_neta": roe_del_cambio_utilidad,
        "cambio_equity": roe_del_cambio_equity,
        "roe_escenario": resultado_escenario.roe,
    }
