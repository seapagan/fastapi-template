# Metrics and Observability

## Overview

The FastAPI Template provides opt-in Prometheus metrics collection for application
observability. This feature allows you to monitor HTTP performance, track authentication
events, and gain insights into API usage patterns.

Metrics are exposed via the `/metrics` endpoint in Prometheus format, making them
compatible with Prometheus, Grafana, and other monitoring tools.

## Enabling Metrics

Metrics collection is **disabled by default** to minimize overhead. To enable:

1. Add to your `.env` file:
   ```bash
   METRICS_ENABLED=true
   ```

2. Restart your application:
   ```bash
   api-admin serve
   ```

3. Access metrics at:
   ```
   http://localhost:8000/metrics
   ```

## Available Metrics

All metrics are prefixed with your `API_TITLE` setting (converted to snake_case)
to prevent naming collisions when running multiple services. For example, with
`API_TITLE="API Template"`, metrics will be prefixed as `api_template_`.

### HTTP Performance Metrics

These metrics track all HTTP requests except `/metrics` and `/heartbeat` endpoints:

**`{api_title}_http_requests_total`**
Total number of HTTP requests.

- Labels: `method` (GET, POST, etc.), `handler` (route path), `status` (2xx, 4xx, etc.)
- Type: Counter
- Example: `api_template_http_requests_total{handler="/users/",method="GET",status="2xx"} 1542`

**`{api_title}_http_request_duration_highr_seconds`**
Request latency histogram with custom buckets optimized for API response times.

- Labels: `method`, `handler`
- Type: Histogram
- Buckets: 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0 seconds
- Use for: P50, P95, P99 latency calculations

**`{api_title}_http_requests_inprogress`**
Current number of in-flight HTTP requests.

- Labels: `method`, `handler`
- Type: Gauge
- Use for: Real-time load monitoring

**`{api_title}_http_request_size_bytes`**
Distribution of HTTP request body sizes.

- Labels: `method`, `handler`
- Type: Summary

**`{api_title}_http_response_size_bytes`**
Distribution of HTTP response body sizes.

- Labels: `method`, `handler`
- Type: Summary

### Business Metrics

Custom application metrics for security and operational insights:

**`{api_title}_auth_failures_total`**
Total authentication failures.

- Labels:
  - `reason`: `expired_token`, `invalid_token`, `banned_user`, `unverified_user`
  - `method`: `jwt`, `refresh_token`
- Type: Counter
- Use for: Detecting brute force attacks, token abuse patterns

**`{api_title}_api_key_validations_total`**
Total API key validation attempts.

- Labels:
  - `status`: `valid`, `invalid_format`, `not_found`, `inactive`, `user_banned`, `user_unverified`
- Type: Counter
- Use for: Monitoring API key adoption, detecting misconfiguration

**`{api_title}_login_attempts_total`**
Total login attempts.

- Labels:
  - `status`: `success`, `invalid_password`, `not_found`, `not_verified`, `banned`
- Type: Counter
- Use for: Security monitoring, UX insights (high password failures may indicate UX issues)

## Accessing Metrics

### Via HTTP

```bash
curl http://localhost:8000/metrics
```

Example output:
```prometheus
# HELP api_template_http_requests_total Total number of HTTP requests
# TYPE api_template_http_requests_total counter
api_template_http_requests_total{handler="/users/",method="GET",status="2xx"} 1542.0

# HELP api_template_auth_failures_total Total authentication failures by reason and method
# TYPE api_template_auth_failures_total counter
api_template_auth_failures_total{method="jwt",reason="expired_token"} 15.0
api_template_auth_failures_total{method="jwt",reason="invalid_token"} 8.0

# HELP api_template_login_attempts_total Total login attempts by status
# TYPE api_template_login_attempts_total counter
api_template_login_attempts_total{status="success"} 892.0
api_template_login_attempts_total{status="invalid_password"} 24.0
```

### Via Prometheus UI

For local development and testing, the project includes a pre-configured Prometheus
setup:

1. Navigate to the `prometheus-test/` directory:
   ```bash
   cd prometheus-test/
   ```

2. Start Prometheus:
   ```bash
   docker compose up
   ```

3. Access the Prometheus UI:
   ```
   http://localhost:9090
   ```

4. Your application metrics will be automatically scraped every 15 seconds

5. Example queries to try:
   ```promql
   # Request rate (per second)
   rate(api_template_http_requests_total[5m])

   # 95th percentile latency
   histogram_quantile(0.95, rate(api_template_http_request_duration_highr_seconds_bucket[5m]))

   # Failed login attempts in last hour
   increase(api_template_login_attempts_total{status="invalid_password"}[1h])
   ```

## Configuration

Metrics behavior is controlled by the `METRICS_ENABLED` environment variable:

- `true` - Metrics collection enabled, `/metrics` endpoint accessible
- `false` (default) - Metrics collection disabled, zero performance overhead

### Metric Namespace

The metric namespace is automatically derived from your `API_TITLE` setting:

- `API_TITLE="API Template"` → `api_template_`
- `API_TITLE="My Cool API"` → `my_cool_api_`

This prevents metric name collisions when running multiple services in the same
Prometheus instance.

### Excluded Endpoints

The following endpoints are excluded from HTTP metrics to prevent noise and
recursive tracking:

- `/metrics` - The metrics endpoint itself
- `/heartbeat` - Health check endpoint

## Performance Impact

- **HTTP Metrics**: Minimal overhead (<1ms per request) from the optimized
  `prometheus-fastapi-instrumentator` library
- **Business Metrics**: Negligible (<1μs) compared to auth operations (typically 100-300ms)
- **When Disabled**: Zero overhead - metrics code is not executed

## Integration Examples

### Grafana Dashboard

Create a dashboard to visualize your metrics:

1. Add Prometheus as a data source in Grafana
2. Create panels with queries like:
   ```promql
   # Request rate by endpoint
   sum by(handler) (rate(api_template_http_requests_total[5m]))

   # Error rate
   sum(rate(api_template_http_requests_total{status=~"4..|5.."}[5m]))
   / sum(rate(api_template_http_requests_total[5m]))
   ```

### Alerting Rules

Example Prometheus alerting rules:

```yaml
groups:
  - name: api_template_alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(api_template_http_requests_total{status=~"5.."}[5m]))
          / sum(rate(api_template_http_requests_total[5m])) > 0.05
        for: 5m
        annotations:
          summary: High 5xx error rate detected

      - alert: AuthenticationFailureSpike
        expr: |
          rate(api_template_auth_failures_total[5m]) > 10
        for: 2m
        annotations:
          summary: Possible brute force attack detected
```

## See Also

- [Project Organization](../project-organization.md#appmetrics) - Metrics module structure
- [Configuration Guide](configuration/environment.md) - All environment variables
- [Prometheus Documentation](https://prometheus.io/docs/introduction/overview/)
