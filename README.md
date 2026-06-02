# AGUACATE Y LIMÓN: Predicción de precios para una comercialización justa (Mercado Justo)

## Descripción del Proyecto

**Mercado Justo** es una iniciativa orientada a reducir la asimetría informacional entre pequeños productores agrícolas y los mercados mayoristas en México. El proyecto utiliza un pipeline avanzado de datos para transformar el histórico de precios del **SNIIM** (2000–2026) en recomendaciones accionables.

El sistema se centra en el **Aguacate Hass** y el **Limón con semilla**, integrando procesamiento distribuido, modelos estadísticos y algoritmos de optimización para responder: ¿dónde, cuándo y a cuánto vender?

## Pipeline del Proyecto

El flujo de trabajo consta de 6 etapas encadenadas:

1.  **Adquisición de Datos**: Web Scraping interactivo del portal SNIIM.
2.  **Análisis Exploratorio (PySpark)**: Caracterización de estacionalidad y distribución de precios.
3.  **Pronóstico SARIMA**: Estimación de precios mensuales para los próximos 12 meses.
4.  **Clasificación Random Forest**: Identificación de momentos favorables de venta por ruta logística.
5.  **Optimización (Dijkstra)**: Determinación de rutas de menor costo ajustadas por probabilidad de precio.
6.  **Plan de Marketing**: Alertas y recomendaciones vía WhatsApp/Correo.

## Tecnologías Principales

-   **Quarto**: Generación de reportes dinámicos e interactivos (`.qmd`).
-   **PySpark**: Procesamiento de datos a gran escala y ML (MLlib).
-   **Docker**: Entorno reproducible basado en `jupyter/pyspark-notebook`.
-   **Statsmodels**: Modelado de series de tiempo (SARIMA).

## Instalación y Uso

### 1. Entorno Docker
El proyecto está diseñado para ejecutarse dentro de un contenedor Docker para asegurar la compatibilidad de Spark y Quarto.

```bash
# Iniciar el contenedor (si ya está creado)
docker start mercado-justo
```

### 2. Ejecución del Análisis
El corazón del análisis reside en `mercado_justo.qmd`. Puedes interactuar con él de dos formas:

-   **Jupyter Lab**: Abre el puerto `8888` para editar y ejecutar las celdas de PySpark.
-   **Renderizado de Quarto**:
    ```bash
    quarto render mercado_justo.qmd --to html
    ```
-   **Spark UI**: Monitorea el procesamiento en tiempo real en el puerto `4040`.

### 3. Recolección de Datos (Script independiente)
Si deseas actualizar los datos manualmente:
```bash
python scrape_sniim.py --start-date 01/01/2024 --end-date 24/04/2026
```

## Estructura de Archivos

-   `mercado_justo.qmd`: Documento principal del análisis y pipeline.
-   `scrape_sniim.py`: Motor de scraping para el SNIIM.
-   `index.html`: Versión renderizada del reporte (Quarto).
-   `sniim_resultados.csv`: Dataset consolidado.
-   `requirements.txt`: Dependencias de Python.

## Datos y Mercados
-   **Fuentes**: SNIIM (2000-2026).
-   **Productos**: Aguacate Hass, Limón con semilla.
-   **Mercados**: Cobertura nacional con énfasis en Michoacán, Veracruz y CDMX.
