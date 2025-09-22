# Observability prompt

## Project Context

I need your help to plan a comprehensive observability solution for my service that has:
  - OpenTelemetry Collector for telemetry data processing
  - Prometheus for metrics storage and querying
  - Grafana for visualization and dashboards
  - cAdvisor for container metrics
  - Docker Compose orchestration
  - Load testing capabilities


## Infrastructure Components

  The target solution includes these Docker services:
  - OpenTelemetry Collector: Centralized telemetry processing (OTLP gRPC/HTTP receivers)
  - Prometheus: Metrics storage with 15s scrape intervals
  - Grafana: Visualization with provisioned dashboards and datasources
  - cAdvisor: Container resource monitoring
  - Application: FastAPI service with health check endpoint

### Key Configuration Files Needed

  1. docker-compose.yml - Orchestrate all observability services
  2. observability/otel-collector.yml - OpenTelemetry Collector configuration
  3. observability/prometheus.yml - Prometheus scraping configuration
  4. observability/grafana/provisioning/ - Auto-provision datasources and dashboards
  5. Load testing tools for validation

## Observability Categories to Implement

  1. Container Resource Monitoring

  - CPU Usage: Container CPU utilization as percentage
  - Memory Usage: Container memory consumption in bytes
  - Data Source: cAdvisor metrics via Prometheus

  2. Application Pool Metrics (if applicable)

  - Database Connection Pools: active, total, idle connections
  - Thread Pools: active, total, idle threads
  - Custom Resource Pools: any bounded resource tracking

  3. Application Health Metrics

  - Health Check: Service availability endpoint
  - Request Metrics: HTTP request rates, latencies, error rates
  - Custom Business Metrics: Application-specific measurements

## Technical Requirements

### Docker Compose Services

#### Services needed:
  - otel-collector (otel/opentelemetry-collector-contrib:latest)
  - prometheus (prom/prometheus:latest)
  - grafana (grafana/grafana:latest)
  - cadvisor (gcr.io/cadvisor/cadvisor:v0.52.0)
  - [your-application-service]

### Port Mappings Required

  - Grafana: 3001:3000 (or 3000:3000)
  - Prometheus: 9090:9090
  - OpenTelemetry Collector: 4317 (gRPC), 4318 (HTTP), 8889 (metrics)
  - cAdvisor: 8080:8080
  - Application: [your-app-port]

### Network Configuration

  - All services on shared Docker network
  - Service discovery via container names
  - Proper dependency ordering with health checks

## Deliverables Requested

  1. Docker Compose Setup
    - Complete docker-compose.yml with all observability services
    - Proper volumes for data persistence
    - Network configuration for service discovery
  2. OpenTelemetry Configuration
    - otel-collector.yml with OTLP receivers
    - Prometheus exporter configuration
    - Resource processing and batching
  3. Prometheus Configuration
    - prometheus.yml with scrape targets for:
        - OpenTelemetry Collector metrics
      - cAdvisor container metrics
      - Application metrics endpoint (if implemented)
    - Appropriate scrape intervals and timeouts
  4. Grafana Setup
    - Provisioned Prometheus datasource
    - Dashboard configuration showing:
        - Container CPU and memory usage
      - Application metrics (if available)
      - Resource utilization trends
    - Auto-import dashboard on startup
  5. Application Integration (if not already implemented)
    - Add /metrics endpoint to your application
    - Basic health check endpoint
    - Optional: Custom metrics collection
  6. Load Testing Tools
    - Simple load generation script
    - Scenarios for testing different resource patterns
    - Integration with Make commands for easy execution
  7. Documentation
    - Setup and usage instructions
    - How to access dashboards (URLs, credentials)
    - How to validate metrics are flowing correctly

## Expected Behavior After Implementation

  1. docker-compose up -d starts entire observability stack
  2. Grafana accessible at http://localhost:3001 (admin/admin)
  3. Prometheus accessible at http://localhost:9090
  4. Container metrics automatically collected and visible in dashboards
  5. Application metrics (if implemented) flowing through OpenTelemetry → Prometheus → Grafana
  6. Load testing generates visible metric changes in dashboards

  Please help me plan this observability implementation staxk step by step, ensuring all components integrate properly and metrics flow correctly from collection through visualization.