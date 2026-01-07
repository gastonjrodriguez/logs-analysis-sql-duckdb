import duckdb

def main():
    con = duckdb.connect()

    con.execute("""
        CREATE TABLE logs AS 
        SELECT * FROM read_json_auto('data/logs_*.json')
    """)

    # Chequeo de carga satisfactoria
    rows_amount = con.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
    print(f"Filas: {rows_amount}")

    # Tipo de dato de los campos
    for col in con.execute("DESCRIBE logs").fetchall():
        print(f"{col[0]}: {col[1]}")

    # Primeras N filas:
    first_rows = con.execute("SELECT * FROM logs LIMIT 5").fetchdf()
    print(f"Primeras filas: \n{first_rows}")


    # EXPLORACION --------------------------------------------------------------------------------------------------------

    initial_summary = con.execute("""
        SELECT COUNT(*) AS requests_amount,
        COUNT(DISTINCT user_id) AS unique_users,
        COUNT(DISTINCT endpoint) AS unique_endpoints,
        MIN(timestamp) AS first_log,
        MAX(timestamp) AS last_log
        FROM logs;
    """).fetchdf()
    print(initial_summary)

    # ENDPOINTS mas usados:
    more_used_endpoints = con.execute("""
        SELECT endpoint,
        COUNT(*) AS hits,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM logs),2) AS percentage_of_use
        FROM logs
        GROUP BY endpoint
        ORDER BY percentage_of_use DESC
        LIMIT 5;
    """).fetchdf()

    print(more_used_endpoints)
    # un 20% de los logs no tiene un endpoint registrado (podria sugerirnos logs incompletos o eventos que no se asocian con rutas HTTP).
    # el resto de los resultados nos dice que no hay un endpoint que domine el trafico, lo cual indica un balance de este ultimo.
    # los hits (es decir los request que recibio el endpoint) nos permiten ser mas finos al apreciar la dominacion del trafico.


    # ERRORES:
    errors_analysis = con.execute("""
        SELECT endpoint,
        COUNT(*) AS error_amount,
        COUNT(DISTINCT user_id) AS affected_users,
        ROUND(AVG(response_time_ms)/1000.0, 2) AS avg_response_time_sec
        FROM logs
        WHERE status_code >= 500
        GROUP BY endpoint
        ORDER BY error_amount DESC
        LIMIT 5;
    """).fetchdf()
    print(errors_analysis)

    # Los endpoints que dan mas errores tienen tambien tiempos de respuesta elevados. Esto afecta a muchos usuarios unicos
    # (posibilidad de problemas de performance/timeouts)


    # PERFORMANCE DE ENDPOINTS:
    # vemos el p50, p95, y p99. Un promedio esconde colas lentas, los percentiles las muestran.
    performance_endpoints = con.execute("""
        SELECT endpoint,
        COUNT(*) AS requests,
        ROUND(AVG(response_time_ms),2) AS avg_response_time,
        ROUND(MAX(response_time_ms),2) AS max_response_time,
        ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY response_time_ms),2) AS p50,
        ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms),2) AS p95,
        ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time_ms),2) AS p99
        FROM logs
        WHERE status_code < 500
        GROUP BY endpoint
        HAVING COUNT(*) > 100
        ORDER BY p95 DESC
        LIMIT 5
    """).fetchdf()
    print(performance_endpoints)

    # status_code < 500 para requests exitosos.
    # HAVING COUNT(*) > 100 para quedarse con los endpoints que tienen un trafico suficiente.
    # el 95% de los requests tardó 478.50 ms o menos. El 99% de los requests tardó 496 ms o menos.
    # Para SLOs (Service Level Objectives) el p95 es mas comun (es mas estable ante eventos raros, tolera outliers que no se pueden evitar, y
    # protege a la mayoria de los users "limitando" cuantos pueden tener una mala experiencia (punto de corte en response time)).
    # El p99 hace mas foco en el 1% de peor experiencia. Se usa mas para problemas poco frecuentes (existen pero no afectan a todos).


    # PICOS HORARIOS:

    trend_per_hours = con.execute("""
        SELECT EXTRACT(HOUR FROM timestamp) AS hour,
        COUNT(*) AS requests,
        SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) AS errors_amount,
        ROUND(AVG(response_time_ms),2) AS avg_response_time
        FROM logs
        GROUP BY EXTRACT(HOUR FROM timestamp)
        ORDER BY requests DESC
    """).fetchdf()
    print(trend_per_hours)

    # A las 5pm es cuando hay mas requests, seguido por las 10am. (ORDER BY requests DESC)
    # A la 1am y 10am es cuando hay mas caudal de errores. (ORDER BY errors_amount DESC)
    # Los tiempos de respuesta son mas elevados a la 1pm y 2pm. (ORDER BY avg_response_time DESC)

    # FLAG -------> Hay nulos en timestamp.
    # double-check de esa flag:
    timestamp_nulls = con.execute("""
        SELECT COUNT(timestamp) AS non_nulls_timestamp,
        COUNT(*) - COUNT(timestamp) AS nulls_in_timestamp
        FROM logs        
    """).fetchdf()
    print(timestamp_nulls)


    # TOP REQUESTS MAS LENTOS (POR ENDPOINT)
    top_slowest_requests = con.execute("""
        WITH ranking AS (
            SELECT endpoint,
            response_time_ms,
            timestamp,
            user_id,
            ROW_NUMBER() OVER (PARTITION BY endpoint ORDER BY response_time_ms DESC) AS rank
            FROM logs
            WHERE status_code < 500 AND timestamp IS NOT NULL
    )
    SELECT *
    FROM ranking
    WHERE rank <= 3
    ORDER BY endpoint, rank
    """).fetchdf()
    print(top_slowest_requests)

    # FLAG -------> Hay user_id que son nulos.
    # Double-check de la flag
    user_id_nulls = con.execute("""
        SELECT COUNT(user_id) AS non_nulls_user_id,
        COUNT(*) - COUNT(user_id) AS nulls_in_user_id
        FROM logs        
    """).fetchdf()
    print(user_id_nulls)

    # CANTIDAD DE ERRORES POR USUARIO:
    errors_per_user = con.execute("""
        WITH users AS (
        SELECT user_id,
        COUNT(user_id) AS errors
        FROM logs
        GROUP BY user_id
    ) 
    SELECT user_id,
    errors,
    DENSE_RANK() OVER (ORDER BY errors DESC) AS ranking
    FROM users
    ORDER BY errors DESC
    LIMIT 10
    """).fetchdf()
    print(errors_per_user)

    # La cantidad de errores no es lo suficientemente significativa como para justificar un análisis más granular (por ejemplo, incorporar analisis de tiempo con el timestamp).


    # FLUCTUACION DE TRAFICO DIA A DIA:
    traffic_fluctuation = con.execute("""
        WITH requests_per_date AS (
            SELECT DATE(timestamp) AS date,
            COUNT(*) AS requests,
            ROUND(AVG(response_time_ms),2) AS avg_response_time
            FROM logs
            WHERE timestamp IS NOT NULL
            GROUP BY DATE(timestamp)
    )
    SELECT date,
    requests,
    LAG(requests) OVER (ORDER BY date) AS prev_requests,
    requests - LAG(requests) OVER (ORDER BY date) AS requests_amount_difference,
    ROUND(((requests - LAG(requests) OVER (ORDER BY date)) * 100.0) / NULLIF(LAG(requests) OVER (ORDER BY date),0),2) AS pct_variation
    FROM requests_per_date
    ORDER BY date
    """).fetchdf()
    print(traffic_fluctuation)


    # NOTA: Se trackearon los nulls solo de campos de relevancia para este analisis, como lo son user_id y timestamp.


    # RECOMENDACIONES PARA EL EQUIPO DE DESARROLLO EN BASE AL ANALISIS:
    # 1) Priorizar endpoints criticos:
    # /api/products, /api/auth/login, /api/users, y /metrics, concentran mas errores y mayores tiempos de respuesta, afectando a muchos usuarios.
    # Se podria hacer foco inicialmente en optimizar performance y manejar errores.

    # 2) Atacar picos horarios problematicos:
    # Hay ciertas franjas horarias con mayor volumen de errores (ej. 1am y 10am) y una mayor latencia (ej. 1pm, 2pm). 10am y 5pm son las franjas con mas requests.
    # Acciones posibles comprenden revisar capacidad, concurrencia, autoscaling y dependencias externas de esos momentos.

    # 3) Mejorar la calidad y consistencia de los logs:
    # Existe una proporcion significativa de logs no tiene al menos uno de los siguientes: endpoint, timestamp, o user_id, lo que limita tanto analisis como debugging.
    # Frente a esto, se podria estandarizar el logging para garantizar campos clave obligatorios y una observabilidad confiable.


if __name__ == "__main__":
    main()