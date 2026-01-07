# Analisis de Logs

Analisis sobre logs de aplicaciones en formato JSON, utilizando DuckDB y queries SQL para evaluar uso de endpoints, errores, performance y patrones temporales.

## Objetivo
Identificar problemas de performance, estabilidad y calidad de logs, y proponer recomendaciones accionables para el equipo de desarrollo.

## Tecnologias
- Python
- DuckDB
- SQL (window functions, percentiles, funciones de agregacion)

## Qué se aplica en este proyecto
- Capacidad para analizar datos (nulls, inconsistencias)
- Uso de SQL avanzado (CTEs, window functions, percentiles)
- Pensamiento orientado a impacto y toma de decisiones
- Comunicación de hallazgos

## Como correr
pip install duckdb
python logs-analysis-duckdb.py

El analisis se ejecuta desde una función `main()` protegida por el bloque:

```python
if __name__ == "__main__":
    main()
```

## Analisis realizado
- Frecuencia de uso y distribución de endpoints
- Analisis de errores y volumen de usuarios afectados
- Performance de endpoints por percentiles (p50, p95, p99)
- Ranking de peor latencia de endpoints
- Analisis de picos horarios de tráfico y caudal de errores
- Calidad de logs

## Principales conclusiones y sugerencias
- Algunos endpoints críticos concentran la mayoria de errores y alta latencia. Se sugiere tomar acciones de optimizacion de performance y manejo de errores.
- Existen franjas horarias con mayor volumen de errores y alta latencia. Se sugiere revisar capacidad, concurrencia, autoscaling y dependencias externas de esos momentos.
- La presencia de valores nulos en campos como timestamp, endpoint, y user_id, limita el análisis y el debugging. Se sugiere estandarizar el logging para garantizar campos clave obligatorios y una observabilidad confiable.

## Autor
Gaston Rodriguez