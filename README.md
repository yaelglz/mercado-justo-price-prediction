# AGUACATE Y LIMÓN: Predicción de precios para una comercialización justa

## Descripción del Proyecto

El presente proyecto responde a la problemática de la volatilidad de precios en productos agrícolas clave mediante el desarrollo de modelos de series de tiempo que pronostiquen precios mensuales de **aguacate** y **limón** en mercados estratégicos de México:
- **Valle de México**
- **Michoacán**
- **Veracruz**

El análisis sistematiza datos oficiales del **SNIIM** (Servicio Nacional de Información e Integración de Mercados), implementando técnicas estadísticas y de machine learning (**ARIMA/SARIMA, Prophet, suavizamiento exponencial, LSTM**) para generar recomendaciones accionables que optimicen la comercialización, reduzcan la volatilidad de ingresos y promuevan prácticas de mercado más equitativas.

## Estructura del Proyecto

1. **Recolección de Datos**: `scrape_sniim.py` - Script para la extracción automática de precios históricos desde el portal del SNIIM.
2. **Análisis y Modelado**: `mercado_justo.ipynb` - Notebook con el análisis exploratorio, preprocesamiento y entrenamiento de modelos predictivos siguiendo la metodología de "Mercado Justo".

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### 1. Recolección automática de SNIIM

El script `scrape_sniim.py` selecciona automáticamente productos que contienen `aguacate` o `limón`, consulta el endpoint de resultados y exporta un CSV consolidado.

```bash
# Ejecución básica (extrae desde 2016 hasta hoy)
python scrape_sniim.py
```

**Opciones útiles:**
- `--output data/mi_archivo.csv`: Cambiar archivo de salida.
- `--start-date 01/01/2024 --end-date 24/04/2026`: Rango de fechas explícito.
- `--rows-per-page 50000`: Optimización de registros por página.
- `--max-products 2`: Prueba rápida con pocos productos.

### 2. Análisis y Predicción

Abra el notebook `mercado_justo.ipynb` en un entorno compatible (Jupyter, VS Code, PyCharm) para visualizar el análisis de:
- Regresión Polinomial
- Regresión Logística
- Árboles de Decisión
- (Y otros modelos de series de tiempo mencionados)

## Datos y Mercados
- **Fuentes**: SNIIM (2016-2026).
- **Productos**: Aguacate Hass, Limón con semilla, Limón sin semilla.
- **Mercados Clave**: CDMX, Morelia, Veracruz.
