from sqlalchemy_collectd.client import collector, worker

from metrics.prometheus_metrics import GuageMetrics


def start_track_pool_metrics(engine, prefix_name):
    track_database(engine, prefix_name,
                   checkedout_connections=GuageMetrics.POSTGRES_CHECKEDOUT_CONNECTIONS,
                   checkedin_connections=GuageMetrics.POSTGRES_CHECKEDIN_CONNECTIONS,
                   total_connections=GuageMetrics.POSTGRES_TOTAL_CONNECTIONS,
                   detached_connections=GuageMetrics.POSTGRES_DETACHED_CONNECTIONS,
                   )


def track_database(
        engine,
        service_name,
        checkedout_connections: GuageMetrics,
        checkedin_connections: GuageMetrics,
        total_connections: GuageMetrics,
        detached_connections: GuageMetrics,
):
    class prometheusSender:
        def send(self, collection_target, timestamp, interval, process_token):
            checkedout_connections.metric.set(collection_target.num_checkedout)
            checkedin_connections.metric.set(collection_target.num_checkedin)
            total_connections.metric.set(collection_target.num_connections)
            detached_connections.metric.set(collection_target.num_detached)

    collection_target = collector.CollectionTarget.collection_for_name(service_name)
    collector.EngineCollector(collection_target, engine)
    sender = prometheusSender()
    worker.add_target(collection_target, sender)
