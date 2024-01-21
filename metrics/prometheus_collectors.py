from prometheus_client import Summary


class MetricStore:
    store = {}

    @classmethod
    def get_collector(cls, name, desc) -> Summary:
        return cls.store.get(name, None) or cls._init_collector(name, desc)

    @classmethod
    def _init_collector(cls, name, desc) -> Summary:
        collector = Summary(name, desc)
        cls.store[name] = collector
        return collector


