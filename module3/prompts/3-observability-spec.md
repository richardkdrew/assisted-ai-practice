# Observability Stack Specification

This document contains details necessary to create a prompt for implementing comprehensive observability for microservices. This specification is based on lessons learned from real implementation challenges and provides actionable guidance to avoid common pitfalls.

The prompt should:
- ask the assistant to create a complete observability implementation plan
- recommend strict adherence to ALL of the details in this document
- strongly encourage the assistant to verify metric label schemas before creating dashboards
- encourage the assistant to test the full stack end-to-end before considering implementation complete

## Tech Stack

| Area                    | Choice                    | Version      | Purpose                           |
|-------------------------|---------------------------|--------------|-----------------------------------|
| Metrics Collection      | Prometheus                | latest       | Time-series metrics storage       |
| Visualization           | Grafana                   | latest       | Dashboard and alerting platform   |
| Container Metrics       | cAdvisor                  | v0.52.0      | Container resource monitoring     |
| Application Tracing     | OpenTelemetry             | >=1.20.0     | Distributed tracing framework     |
| Metrics Export          | OTLP Exporter             | >=1.20.0     | OpenTelemetry metrics export      |
| Business Metrics        | Prometheus Client         | >=0.17.0     | Application-specific metrics      |
| Containerization        | Docker Compose            | latest       | Multi-service orchestration       |

## Architecture Components

### Core Services
1. **Application Service** - The service being monitored
2. **Prometheus** - Metrics collection and storage (port 9090)
3. **Grafana** - Visualization and dashboards (port 3001)
4. **cAdvisor** - Container metrics collection (port 8080)
5. **OpenTelemetry Collector** - Telemetry data processing (port 4317)

### Service Dependencies
- Application Service → exposes `/metrics` endpoint
- Prometheus → scrapes metrics from Application Service and cAdvisor
- Grafana → queries Prometheus for dashboard data
- OpenTelemetry Collector → receives telemetry from Application Service

## Critical Implementation Requirements

### 1. Metrics Schema Validation
**MUST** verify actual metric label schemas before creating dashboard queries:

```bash
# Always verify cAdvisor metric labels
curl -s http://localhost:8080/metrics | grep container_cpu_usage_seconds_total | head -3

# Check actual label structure (common issue: name vs id labels)
# cAdvisor uses 'id' labels like: id="/docker/container_id_here"
# NOT 'name' labels like: name="container-name"
```

### 2. Dashboard Query Patterns
**Container Metrics** - Use `id` labels, not `name` labels:
```promql
# CORRECT - matches cAdvisor's actual label schema
rate(container_cpu_usage_seconds_total{id=~"/docker/.*"}[5m]) * 100

# INCORRECT - assumes name labels that may not exist
rate(container_cpu_usage_seconds_total{name="service-name"}[5m]) * 100
```

**Business Metrics** - Implement manual update mechanism:
```python
# Provide both automatic and manual metric updates
async def _update_metrics():
    app_count = await app_repository.count()
    config_count = await config_repository.count()
    update_business_metrics(app_count, config_count, get_db_connections())

# Add to application creation/deletion endpoints
```

### 3. Docker Compose Configuration

**Required Services:**
```yaml
services:
  app:
    build: .
    ports: ["8000:8000"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    depends_on:
      postgres:
        condition: service_healthy

  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes:
      - ./observability/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports: ["3001:3000"]
    volumes:
      - ./observability/grafana/provisioning:/etc/grafana/provisioning
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.52.0
    ports: ["8080:8080"]
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
```

## Instrumentation Requirements

### Application Metrics Endpoint
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Business metrics (updated by application logic)
APP_COUNT = Gauge('applications_total', 'Total number of applications')
CONFIG_COUNT = Gauge('configurations_total', 'Total number of configurations')
DB_CONNECTIONS = Gauge('database_connections_active', 'Active database connections')

# HTTP metrics (updated by middleware)
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests',
                       ['method', 'endpoint', 'status_code'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration',
                           ['method', 'endpoint'])

@app.get("/metrics")
async def metrics_endpoint():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

### OpenTelemetry Integration
```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

def setup_observability(app):
    # Instrument FastAPI automatically
    FastAPIInstrumentor.instrument_app(app)

    # Instrument database connections
    Psycopg2Instrumentor().instrument()

    # Add custom middleware for business metrics
    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        # Record HTTP metrics here
        pass
```

## Dashboard Specifications

### Required Dashboards

1. **Application Metrics Dashboard**
   - HTTP request rate and duration
   - Business metrics (applications, configurations, database connections)
   - Error rates by endpoint
   - Service health status

2. **Container Metrics Dashboard**
   - CPU usage per container
   - Memory usage per container
   - Network I/O rates
   - Container restart counts

### Dashboard JSON Requirements
- Use Grafana's dashboard JSON format (not wrapped in "dashboard" object)
- Place in `observability/grafana/provisioning/dashboards/`
- Use auto-provisioning to avoid manual dashboard imports

## Validation Checklist

### Before Implementation Complete:
- [ ] Verify `/metrics` endpoint returns Prometheus format
- [ ] Confirm cAdvisor metric label schema matches dashboard queries
- [ ] Test business metrics update automatically when data changes
- [ ] Validate dashboard queries return data in Prometheus
- [ ] Ensure Docker Compose stack starts all services healthy
- [ ] Verify Grafana auto-provisions dashboards correctly
- [ ] Test manual metrics update via debug endpoint

### Common Pitfalls to Avoid:

1. **Label Schema Mismatch**: Always verify actual metric labels before writing queries
2. **Static Business Metrics**: Ensure metrics update when application state changes
3. **Dashboard Import Issues**: Use auto-provisioning with correct JSON format
4. **Container ID vs Name**: Use `id` labels for cAdvisor metrics, not `name`
5. **Missing Dependencies**: Include observability extras in dependency management
6. **Docker Image Staleness**: Rebuild Docker images after code changes
7. **Health Check Failures**: Implement proper health checks for service dependencies

## File Structure

```
observability/
├── prometheus/
│   └── prometheus.yml           # Prometheus configuration
├── grafana/
│   ├── grafana.ini             # Grafana configuration
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml   # Prometheus datasource
│       └── dashboards/
│           ├── dashboards.yml   # Dashboard provider config
│           ├── application-metrics.json
│           └── container-metrics.json
└── docker-compose.yml          # Full stack orchestration
```

## Testing Strategy

### Integration Testing
- Test against full Docker Compose stack, not individual services
- Verify metrics collection end-to-end
- Validate dashboard functionality with real data
- Test service recovery and metric continuity

### Manual Testing Commands
```bash
# Test metrics endpoint
curl http://localhost:8000/metrics

# Test Prometheus queries
curl 'http://localhost:9090/api/v1/query?query=http_requests_total'

# Test business metrics update
curl -X POST http://localhost:8000/debug/update-metrics

# Verify dashboard data
# Check Grafana at http://localhost:3001 (admin/admin)
```

## Debugging Guidelines

1. **No Dashboard Data**: Check Prometheus targets and scrape health
2. **Container Metrics Missing**: Verify cAdvisor label schema and queries
3. **Business Metrics Zero**: Ensure metrics update functions are called
4. **Service Discovery Issues**: Check Docker Compose service names and networks
5. **Dashboard Not Loading**: Verify JSON format and auto-provisioning configuration

## Performance Considerations

- Set appropriate scrape intervals (default: 15s)
- Configure metric retention policies
- Use metric filtering to reduce cardinality
- Implement proper alerting thresholds
- Monitor observability stack resource usage

## Security Requirements

- Use read-only database connections for metrics collection
- Implement proper network segmentation
- Secure Grafana with authentication
- Avoid exposing sensitive data in metric labels
- Use secure communication between services

## Notes

1. Always verify actual metric schemas before implementing dashboards
2. Test the complete observability stack, not individual components
3. Implement both automatic and manual metric update mechanisms
4. Use Docker Compose for consistent multi-service deployment
5. Plan for metric cardinality and storage requirements
6. Implement proper service health checks and dependencies
7. Document metric meanings and expected ranges for operators