import prometheus_client

# grafana json for this metrics https://github.com/kulaginds/sqlalchemy-prometheus

POSTGRES_CHECKEDOUT_CONNECTIONS = prometheus_client.Gauge(
    "postgres_pool_active_connections", "Number of active postgres connections in pool"
)

POSTGRES_CHECKEDIN_CONNECTIONS = prometheus_client.Gauge(
    "postgres_pool_idle_connections", "Number of idle postgres connections in pool"
)

POSTGRES_TOTAL_CONNECTIONS = prometheus_client.Gauge(
    "postgres_pool_total_connections", "Number of all postgres connections in pool"
)

POSTGRES_DETACHED_CONNECTIONS = prometheus_client.Gauge(
    "postgres_detached_connections", "Number of detached from pool active connections"
)

POSTGRES_CHECKOUTS_COUNT = prometheus_client.Counter(
    "postgres_pool_checkout_count", "Count of checkout connections from pool"
)

POSTGRES_INVALIDATED_COUNT = prometheus_client.Counter(
    "postgres_pool_invalidated_count", "Count of invalidated connections in pool"
)

POSTGRES_CONNECTS_COUNT = prometheus_client.Counter(
    "postgres_pool_connects", "Count of connects in pool"
)

POSTGRES_DISCONNECTS_COUNT = prometheus_client.Counter(
    "postgres_pool_disconnects", "Count of disconnects in pool"
)
