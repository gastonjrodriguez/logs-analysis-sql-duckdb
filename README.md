# Log Analysis

Analysis of application logs in JSON format, using DuckDB and SQL queries to evaluate endpoint usage, errors, performance, and temporal patterns.

## Objective

Identify issues related to performance, stability, and log quality, and propose actionable recommendations for the development team.

## Technologies

- Python
- DuckDB
- SQL (window functions, percentiles, aggregate functions)

## What is applied in this project

- Ability to analyze data (nulls, inconsistencies)
- Use of advanced SQL (CTEs, window functions, percentiles)
- Impact-oriented thinking and decision-making
- Communication of findings

## How to run

```
pip install duckdb
python logs-analysis-duckdb.py
```

The analysis runs from a `main()` function protected by the block:

```python
if __name__ == "__main__":
    main()
```

## Analysis
- Usage frequency and distribution of endpoints
- Analysis of errors and volume of affected users
- Endpoint performance by percentiles (p50, p95, p99)
- Ranking of endpoints with the worst latency
- Analysis of hourly traffic peaks and error rates
- Log quality

## Key findings and recommendations

- Some critical endpoints account for the majority of errors and high latency. We recommend taking steps to optimize performance and manage errors.
- There are specific time slots with higher error volumes and high latency. We recommend reviewing capacity, concurrency, autoscaling and external dependencies during those times.
- The presence of null values in fields such as timestamp, endpoint, and user_id limits analysis and debugging. It is recommended to standardize logging to ensure mandatory key fields and reliable observability.

## Author

Gaston Rodriguez