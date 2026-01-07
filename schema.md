## RELACIONES:

deployments.service_id -> services.service_id
access_logs.service_id -> services.service_id
access_logs.server_id -> servers.server_id
error_logs.service_id -> services.service_id
error_logs.server_id -> servers.server_id
performance_metrics.service_id -> services.service_id
performance_metrics.server_id -> servers.server_id
alert_rules.service_id -> services.service_id
alerts.rule_id -> alert_rules.rule_id


## ESQUEMA DE TABLAS:

### services:
service_id (PK), service_name, description, team, language, repository_url, current_version, is_critical, created_at
### servers:
server_id (PK), hostname, ip_address, region, availability_zone, instance_type, cpu_cores, memory_gb, disk_gb, status, launched_at
### deployments:
deployment_id (PK), service_id (FK), version, environment, deployed_by, deployed_at, status, duration_seconds, commit_sha, rollback_version
### access_logs:
log_id (PK), timestamp, service_id (FK), server_id (FK), trace_id, span_id, method, endpoint, status_code, response_time_ms, request_size_bytes, response_size_bytes, user_agent, client_ip, user_id
### error_logs:
error_id (PK), timestamp, service_id (FK), server_id (FK), error_type, error_message, stack_trace, severity, is_resolved, resolved_at
### performance_metrics:
metric_id (PK), timestamp, service_id (FK), server_id (FK), metric_name, value, unit
### alert_rules:
rule_id (PK), name, service_id (FK), metric_name, condition, threshold, severity, is_enabled, notification_channel
### alerts:
alert_id (PK), rule_id (FK), triggered_at, resolved_at, status, acknowledged_by
### incidents:
incident_id (PK), title, severity, status, started_at, resolved_at, root_cause, services_affected, assigned_to
### on_call_schedules:
schedule_id (PK), week_start, week_end, primary_engineer, secondary_engineer, team


