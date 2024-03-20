import itertools
from abc import abstractmethod, ABC
from typing import List

from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from common.config_controller import Config
from database.schemas import BaseORM


class MergeStrategy(ABC):
    def __init__(self):
        self._log = Config.get_logger("database.MergeStrategy")
        self.batch_size = Config().data["database"]["merge_batch_size"]

    @abstractmethod
    def merge(self) -> None: ...

    @staticmethod
    def _partition(arr: List, size: int):
        for i in range(0, len(arr), size):
            yield list(itertools.islice(arr, i, i + size))

    @staticmethod
    def _get_pk_columns(_model: BaseORM) -> List[str]:
        keys = [column.key for column in inspect(_model).primary_key]
        keys = list(keys)
        keys.sort()
        return keys

    @staticmethod
    def _get_non_pk_columns(_model: BaseORM) -> List[str]:
        attr_names = [c_attr.key for c_attr in inspect(_model).mapper.column_attrs]
        result = [i for i in attr_names if i not in MergeStrategy._get_pk_columns(_model)]
        if "id" in result:
            result.remove("id")  # кастыль но ладно, нужно, если id не отмечен как pk
        return result

    @staticmethod
    def _orm_to_dict(model_instance: BaseORM) -> dict:
        if hasattr(model_instance, '__table__'):
            dict_result = {}
            for c in model_instance.__table__.columns:
                value = getattr(model_instance, c.name)

                if value is not None:
                    dict_result[c.name] = value

            return dict_result


class PostgresMergeStrategy(MergeStrategy):
    def __init__(self, entries: List[BaseORM], s: Session):
        super().__init__()
        self.entries = entries
        self.session = s
        if len(entries) > 0:
            self.model = entries[0].__class__

    def merge(self):
        if len(self.entries) > 0:
            self._merge()
        else:
            self._log.warning(f"Empty merge")

    def _merge(self) -> None:
        list_dict_entries = list(map(lambda x: self._orm_to_dict(x), self.entries))
        batches = list(self._partition(list_dict_entries, self.batch_size))

        for batch in batches:
            if len(batch) < 0:
                continue

            stmt = insert(self.model).values(batch)

            set_stmt = {}
            for column in self.get_columns_for_updating(batch):
                _K = getattr(self.model, column)
                _V = getattr(stmt.excluded, column)
                set_stmt[_K] = _V

            stmt = stmt.on_conflict_do_update(index_elements=self._get_pk_columns(self.model), set_=set_stmt)
            self.session.execute(stmt)

    def get_columns_for_updating(self, batch) -> List[str]:
        columns_for_update = self._get_non_pk_columns(self.model)
        return [c for c in columns_for_update if c in batch[0].keys()]




