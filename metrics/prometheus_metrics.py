import traceback
from enum import Enum
from functools import wraps

from prometheus_client import Summary, Gauge, Counter


class TimeMetrics(Enum):
    SQLALCHEMY = ("sqlalchemy_metrics", "Durations of executing sql requests in seconds")
    ETL_TIME = ("etl_time_metrics", "Durations of executing an etl task")
    ACHIEVE_TIME = ("achieve_time_metrics", "Durations of executing an achieve")

    def __new__(cls, name, describe):
        obj = object.__new__(cls)
        obj._value_ = name
        obj.metric = Summary(name, describe, labelnames=("name", "describe"))
        return obj


class StatusMetrics(Enum):

    ETL_STATUS = "etl_status_metric"
    ACHIEVE_STATUS = "achieve_status_metric"

    def __new__(cls, name):
        obj = object.__new__(cls)
        describe = "+1 - Good, -1 - ERROR"
        obj._value_ = name
        obj.metric = Gauge(name, describe, labelnames=("name", "describe"))
        return obj


class ErrorMetric(Enum):
    ETL = "etl_error_metric"
    ACHIEVE = "achieve_error_metric"

    def __new__(cls, name):
        obj = object.__new__(cls)
        describe = "Monitoring errors and text describing ones"
        obj._value_ = name
        obj.metric = Counter(name, describe, labelnames=("name", "describe", "error_text", "traceback"))
        return obj



class GuageMetrics(Enum):
    POSTGRES_CHECKEDOUT_CONNECTIONS = (
        "postgres_pool_active_connections", "Number of active postgres connections in pool"
    )
    POSTGRES_CHECKEDIN_CONNECTIONS = (
        "postgres_pool_idle_connections", "Number of idle postgres connections in pool"
    )
    POSTGRES_TOTAL_CONNECTIONS = (
        "postgres_pool_total_connections", "Number of all postgres connections in pool",
    )
    POSTGRES_DETACHED_CONNECTIONS = (
        "postgres_detached_connections", "Number of detached from pool active connections"
    )

    def __new__(cls, name, describe):
        obj = object.__new__(cls)
        obj._value_ = name
        obj.metric = Gauge(name, describe)
        return obj


def fix_metric_name(name: str) -> str:
    metric_name = name.lower()
    list_restricted_chars = " \t\n\r\"'\\,.:;=*!-+<>1234567890(){}[]|йцукенгшщзхъфывапролджэячсмитьбюё"
    name = metric_name.translate({ord(ch): '' for ch in list_restricted_chars})
    if len(name) > 100:
        name = name[:50] + "___" + name[len(name) - 50:]
    return name


def time_metric_wrapper(metric: TimeMetrics):
    def decorator(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            metric_label = kwargs.get("metric_label", None)
            if metric_label is None:
                raise ValueError("You should set metric_label='<name>'")

            fixed_metric_name = fix_metric_name(metric_label)
            describe = metric_label
            timer = metric.metric.time()
            timer.labels(name=fixed_metric_name, describe=describe)
            with timer:
                return function(self, *args, **kwargs)

        return wrapper

    return decorator


def status_metric_wrapper(status_metric: StatusMetrics, error_metric: ErrorMetric):
    def decorator(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            metric_label = kwargs.get("metric_label", None)
            if metric_label is None:
                raise ValueError("You should set metric_label='<name>'")

            fixed_metric_name = fix_metric_name(metric_label)
            describe = metric_label
            try:
                result = function(self, *args, **kwargs)
                status_metric.metric.labels(name=fixed_metric_name, describe=describe).set(1)
                return result
            except Exception as e:
                error_text = str(e)
                traceback_str = ''.join(traceback.format_tb(e.__traceback__))
                status_metric.metric.labels(name=fixed_metric_name, describe=describe).set(-1)
                error_metric.metric.labels(name=fixed_metric_name, describe=describe, error_text=error_text,
                                           traceback=traceback_str).inc(1)
                raise e

        return wrapper

    return decorator
