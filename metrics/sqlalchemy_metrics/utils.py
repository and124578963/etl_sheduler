from sqlalchemy_collectd.client import collector, worker
from metrics.prometheus_collectors import MetricStore
from metrics.sqlalchemy_metrics.prometheus_metrics import *


def db_execute_metric_wrapper(function):
    def wrapper(self, statement, **kwargs):
        raw_sql = str(statement.compile())
        list_restricted_chars = " \n\r\",.=:*"
        _name = raw_sql.translate({ord(ch): '' for ch in list_restricted_chars})
        name = _name[:50] + "___" + _name[len(_name) - 50:]
        describe = raw_sql
        timer = MetricStore.get_collector(name, describe).time()
        with timer:
            return function(self, statement, **kwargs)

    return wrapper


def start_track_pool_metrics(engine, prefix_name):
    track_database(engine, prefix_name,
                   checkedout_connections_metric=POSTGRES_CHECKEDOUT_CONNECTIONS,
                   checkedin_connections_metric=POSTGRES_CHECKEDIN_CONNECTIONS,
                   total_connections_metric=POSTGRES_TOTAL_CONNECTIONS,
                   detached_connections_metric=POSTGRES_DETACHED_CONNECTIONS,
                   checkouts_count_metric=POSTGRES_CHECKOUTS_COUNT,
                   invalidated_count_metric=POSTGRES_INVALIDATED_COUNT,
                   connects_count_metric=POSTGRES_CONNECTS_COUNT,
                   disconnects_count_metric=POSTGRES_DISCONNECTS_COUNT,
                   )


def track_database(
        engine,
        service_name,
        checkedout_connections_metric: prometheus_client.Gauge,
        checkedin_connections_metric: prometheus_client.Gauge,
        total_connections_metric: prometheus_client.Gauge,
        detached_connections_metric: prometheus_client.Gauge,
        checkouts_count_metric: prometheus_client.Counter,
        invalidated_count_metric: prometheus_client.Counter,
        connects_count_metric: prometheus_client.Counter,
        disconnects_count_metric: prometheus_client.Counter,
):
    class prometheusSender:

        def __init__(self):
            self.last_checkouts = 0
            self.last_invalidated = 0
            self.last_connects = 0
            self.last_disconnects = 0

        def send(self, collection_target, timestamp, interval, process_token):
            checkedout_connections_metric.set(collection_target.num_checkedout)
            checkedin_connections_metric.set(collection_target.num_checkedin)
            total_connections_metric.set(collection_target.num_connections)
            detached_connections_metric.set(collection_target.num_detached)
            checkouts_count_metric.inc(collection_target.total_checkouts - self.last_checkouts)
            invalidated_count_metric.inc(collection_target.total_invalidated - self.last_invalidated)
            connects_count_metric.inc(collection_target.total_connects - self.last_connects)
            disconnects_count_metric.inc(collection_target.total_disconnects - self.last_disconnects)

            self.last_checkouts = collection_target.total_checkouts
            self.last_invalidated = collection_target.total_invalidated
            self.last_connects = collection_target.total_connects
            self.last_disconnects = collection_target.total_disconnects

    collection_target = collector.CollectionTarget.collection_for_name(service_name)
    collector.EngineCollector(collection_target, engine)
    sender = prometheusSender()
    worker.add_target(collection_target, sender)
