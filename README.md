# Oracle FIn Sim Demo

## 🏦 Simulador de Performance Financiera Bancaria

Una aplicación web ejecutiva para demostrar el concepto de un **Digital Twin Financiero Simplificado** para bancos. Permite simular el impacto de cambios en variables clave sobre KPIs financieros en tiempo real.

---

## 📋 Características Principales

✅ **Simulación Interactiva**: Ajusta 8+ variables clave y ve el impacto inmediato en KPIs  
✅ **Análisis Ejecutivo**: Resumen claro de ROE, ROA, Utilidad, Márgenes, Riesgos  
✅ **Insights Automáticos**: Alertas y recomendaciones basadas en umbrales configurables  
✅ **Gráficos Profesionales**: Comparativos, waterfall de ROE, proyecciones 12 meses  
✅ **Modelos de Sensibilidad**: Relaciones macro-financieras (inflación, desempleo, tasas) → mora  
✅ **Exportación de Escenarios**: Descarga resultados en CSV  
✅ **Diseño Ejecutivo**: Estilo McKinsey/BCG, interfaz limpia y sobria  
✅ **100% Local**: Sin bases de datos, sin autenticación, todo con CSVs editables  

---

## 🚀 Instalación Rápida

### 1. Clonar o descargar el proyecto

```bash
git clone https://github.com/tuusuario/Oracle_FIn_Sim_Demo.git
cd Oracle_FIn_Sim_Demo
```

### 2. Crear ambiente virtual (opcional pero recomendado)

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

La app se abrirá en `http://localhost:8501`.

---

## 📁 Estructura de Archivos

```
Oracle_FIn_Sim_Demo/
├── app.py                    # Interfaz principal (Streamlit)
├── model.py                  # Motor de cálculos financieros
├── utils.py                  # Utilidades: carga datos, formateo, insights
├── requirements.txt          # Dependencias Python
├── README.md                 # Este archivo
└── data/
    ├── escenarios.csv        # Escenarios predefinidos
    ├── sensibilidades.csv    # Coeficientes de sensibilidad macro
    └── configuracion_ui.csv  # Configuración de la UI (textos, metas)
```

---

## 🎮 Cómo Usar la App

### 1. **Seleccionar Escenario Base** (Sidebar)

Elige uno de los 5 escenarios predefinidos:
- **Base**: Caso neutral
- **Expansión Comercial**: Crecimiento de cartera
- **Shock Macro Adverso**: Inflación y desempleo altos
- **Suba de Tasas**: Aumento de tasas activas
- **Estrés de Mora**: Deterioro de calidad crediticia

### 2. **Ajustar Variables de Simulación** (Sliders)

Modifica en tiempo real:
- **Tasa Activa** (en basis points)
- **Costo de Fondeo** (en basis points)
- **Crecimiento de Cartera** (en %)
- **Mora** (en %)
- **Inflación, Desempleo** (en %)
- **Ingresos por Fees, Costos Operativos** (variación %)

### 3. **Ver Resultados** (Main)

Los cambios se calculan automaticamente:
- **KPIs principales** en tarjetas (ROE, ROA, Utilidad, etc.)
- **Tabla comparativa** (Base vs Escenario)
- **Alertas e insights** automáticos
- **Gráficos** de comparación, waterfall, proyecciones

### 4. **Descargar** (Sidebar)

Haz clic en "💾 Descargar CSV" para exportar el escenario simulado.

### 5. **Restablecer** (Sidebar)

Vuelve al escenario base con un clic.

---

## 📊 Modelo Financiero Explícito

### Variables Base (Inputs)

| Variable | Descripción |
|----------|-------------|
| `cartera_total` | Créditos vigentes (USD) |
| `tasa_activa` | Tasa promedio de créditos (%) |
| `costo_fondeo` | Costo promedio de pasivos (%) |
| `mora_base` | Cartera en mora sin ajuste (%) |
| `lgd` | Loss Given Default (%) |
| `ingresos_comisiones` | Ingresos por servicios (USD) |
| `costos_operativos` | Gastos de administración (USD) |
| `equity` | Patrimonio (USD) |
| `activos_totales` | Total de activos (USD) |
| `tasa_impuestos` | Impuesto a la renta (%) |
| `inflacion` | Inflación esperada (%) |
| `desempleo` | Tasa de desempleo (%) |

### Fórmulas Clave

```
Ingresos por Intereses = Cartera × Tasa Activa

Margen Financiero = Ingresos por Intereses - Costo de Fondeo

Mora Ajustada = Mora Base 
               + Sensibilidad_Tasa × ΔTasa
               + Sensibilidad_Desempleo × ΔDesempleo
               + Sensibilidad_Inflación × ΔInflación
               
Provisiones = Cartera × Mora Ajustada × LGD

Ingreso Total = Margen Financiero + Comisiones

Utilidad Neta = (Ingreso Total - Provisiones - Costos Op.) × (1 - Tasa Impuestos)

ROE = Utilidad Neta / Equity

ROA = Utilidad Neta / Activos Totales

NIM = Margen Financiero / Activos Totales

Ratio Eficiencia = Costos Operativos / Ingreso Total
```

### Sensibilidades Macro (Configurables)

Las sensibilidades permiten modelar cómo variables macro afectan la mora:

```
sensibilidad_tasa_mora = -0.005        # Suba de tasa → baja mora
sensibilidad_desempleo_mora = 0.025    # Suba desempleo → sube mora
sensibilidad_inflacion_mora = 0.010    # Suba inflación → sube mora
```

---

## 🗂️ Archivos CSV Editables

### `data/escenarios.csv`

Contiene 5 escenarios predefinidos. Puedes:
- Editar valores de escenarios existentes
- Agregar nuevos escenarios (copiar una fila)

**Columnas**:
- `nombre_escenario`: Nombre único del escenario
- Resto de parámetros financieros y macro

**Ejemplo**: Para agregar "Crecimiento Moderado", copia la fila "Base" y ajusta valores.

### `data/sensibilidades.csv`

Coeficientes que relacionan variables macro con rata de mora.

**Columnas**:
- `parametro`: Nombre del coeficiente
- `valor`: Valor numérico

**Modificar**: Abre el CSV y ajusta los valores según análisis de sensibilidad.

### `data/configuracion_ui.csv`

Textos, etiquetas y umbrales de alertas.

**Columnas**:
- `clave`: Clave de configuración
- `valor`: Valor

**Ejemplos**:
- `titulo_app`: Título visible en la app
- `roe_objetivo_default`: ROE objetivo para alertas
- `mora_critica`: Umbral de mora crítica (→ alerta roja)

---

## 🎨 Personalización

### Cambiar Colores

Edita la sección `<style>` en `app.py`:

```python
--primary: #1B3A6B        # Azul ejecutivo
--accent-green: #0F7B55   # Verde para positivo
--accent-red: #C0392B     # Rojo para negativo
```

### Cambiar Títulos y Textos

Simplemente edita `data/configuracion_ui.csv`:

```
titulo_app,Mi Nuevo Título
subtitulo_app,Mi subtítulo personalizado
```

### Agregar Escenarios

1. Abre `data/escenarios.csv`
2. Copia una fila
3. Cambia `nombre_escenario` y ajusta parámetros
4. Guarda (UTF-8, no BOM)
5. Recarga la app

### Agregar Variables a Simulación

1. En `app.py`, busca "Ajustes de Simulación"
2. Agrega un `st.slider()` nueva
3. Usa el valor en la construcción de `escenario_simulado`
4. Recalcula automáticamente

---

## 📈 Mejoras Futuras (Roadmap v2.0)

- [ ] Segmentación por tipo de producto (hipotecario, consumo, PyME)
- [ ] Simulación multi-país con variables locales
- [ ] Análisis de riesgo de liquidez y capital regulatorio
- [ ] Determinación optimizada de precios
- [ ] Integración con APIs externas (datos macro reales)
- [ ] Dashboard Power BI / Tableau
- [ ] Base de datos persistente (PostgreSQL)
- [ ] Sistema de usuarios y historial de simulaciones
- [ ] Mobile-friendly responsive
- [ ] ML: predicción de mortalidad de escenarios

---

## 🛠️ Stack Técnico

| Componente | Tecnología |
|-----------|-----------|
| **Framework Web** | Streamlit 1.32+ |
| **Cálculo Financiero** | Python + Pandas + NumPy |
| **Visualización** | Plotly |
| **Datos** | CSV (editables) |
| **Ambiente** | Local (sin servidor) |

---

## 📞 Soporte y Cambios

- Para cambios en lógica financiera: edita `model.py`
- Para cambios en carga de datos: edita `utils.py`
- Para cambios de UI: edita `app.py` (sección de CSS)
- Para nuevos datos: edita los CSVs en `data/`

---

## 📄 Licencia

Proyecto de demostración. Libre para uso comercial y modificación.

---

**Creado por**: Tu Nombre / Tu Empresa  
**Versión**: 1.0  
**Última actualización**: Marzo 2026

