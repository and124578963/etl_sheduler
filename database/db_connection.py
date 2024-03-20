import os
from typing import List, Dict, Type, Any

import sqlalchemy as db
from sqlalchemy import select, update, text, Row
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql.ddl import CreateSchema
from sqlalchemy.sql.elements import OperatorExpression

from common.config_controller import Config
from database.merge_strategy import PostgresMergeStrategy
from database.schemas import *
from common.utils import T, Singleton
from metrics.prometheus_metrics import time_metric_wrapper, TimeMetrics

from metrics.sqlalchemy_metrics.utils import start_track_pool_metrics


class PostgresDB(metaclass=Singleton):
    def __init__(self):
        self._logger = Config.get_logger("database")
        self._engine = self._create_engine(username=os.getenv('POSTGRES_USER'),
                                           password=os.getenv('POSTGRES_PASSWORD'),
                                           host=os.getenv('POSTGRES_HOST'),
                                           port=os.getenv('POSTGRES_PORT'),
                                           db_name=os.getenv('POSTGRES_DB'),
                                           pool_size=20
                                           )

        start_track_pool_metrics(self._engine, "gamification")

    def _create_engine(self, username: str, password: str, host: str, port: str, db_name: str,
                       pool_size: int) -> db.Engine:
        db_url = f"postgresql://{username}:{password}@{host}:{port}/{db_name}"
        self._logger.debug(db_url.replace(password, "hidden"))
        return db.create_engine(db_url, pool_size=pool_size)

    def get_engine(self):
        return self._engine

    def create_if_not_exist_metadata(self):
        connection = self._engine.connect()
        for schema in Schema:
            if not self._engine.dialect.has_schema(connection, schema.value):
                connection.execute(CreateSchema(schema.value))
        connection.commit()
        connection.close()

        BaseORM.metadata.create_all(self._engine)

        lsit_view = list(BaseView.instances)
        lsit_view.sort(key=lambda o: o.priority)
        for i in lsit_view:
            i: BaseView
            if not i.is_exist(self._engine):
                self.execute_raw_sql(i.get_sql())
                self._logger.info(f"View {i.schema}.{i.name} пересоздана.")


    @property
    def session(self) -> Session:
        return sessionmaker(bind=self._engine)()

    def truncate_orm_table(self, table: BaseORM):
        self._execute(select(table).delete())
        self._logger.debug(f'Таблица {table.__tablename__} очищена.')

    def update_orm_obj(self, orm_obj: BaseORM, session: Session = None):
        is_temp_session = False
        if session is None:
            session = self.session
            is_temp_session = True

        self._add(orm_obj, session=session, close_session=is_temp_session,
                  metric_label=f"update_{orm_obj.__tablename__}")
        self._logger.debug(f'Updated {orm_obj.__tablename__} values: {orm_obj.__dict__} ')

    def insert_orm_obj(self, orm_obj: BaseORM):
        self._add(orm_obj, metric_label=f"insert_{orm_obj.__tablename__}")
        self._logger.debug(f'Inserted into {orm_obj.__tablename__} data: {orm_obj.__dict__} ')

    def delete_orm_obj(self, orm_obj: BaseORM, session: Session = None):
        temp_session = False
        if session is None:
            temp_session = True

        self._delete(orm_obj, metric_label=f"delete_from_{orm_obj.__tablename__}", session=session,
                     close_session=temp_session)
        self._logger.debug(f'{orm_obj.__dict__} deleted from {orm_obj.__tablename__}')

    def select_orm(self, orm_class: Type[T], conditions: List[OperatorExpression] = None,
                   session: Session = None) -> List[T]:
        conditions = conditions or []

        is_temp_session = False
        if session is None:
            session = self.session
            is_temp_session = True

        statement_builder = select(orm_class)
        for cond in conditions:
            statement_builder = statement_builder.where(cond)
        metric_label = str(statement_builder.compile())
        orm_objects: List[T] = [i for i in self._execute(statement_builder, session=session,
                                                         close_session=is_temp_session, metric_label=metric_label)]

        return orm_objects

    def update_orm(self, orm_class: Type[BaseORM], values: Dict[str, OperatorExpression],
                   conditions: List[OperatorExpression] = None):
        conditions = conditions or []

        statement_builder = update(orm_class)
        for cond in conditions:
            statement_builder = statement_builder.where(cond)

        statement_builder = statement_builder.values(**values)
        metric_label = str(statement_builder.compile())
        self._execute(statement_builder, metric_label=metric_label)

    def execute_raw_sql(self, sql: str) -> list[Row[Any]]:
        return self._execute(text(sql), metric_label=sql, is_raw=True)

    def merge_orm_obj(self, orm_obj: BaseORM):
        metric_label = f"single_merge_{orm_obj.__tablename__}"
        self._merge([orm_obj, ], metric_label=metric_label)

    def merge_batch_orm_obj(self, orm_objs: List[BaseORM]):
        if len(orm_objs) > 0:
            metric_label = f"batch_merge_{orm_objs[0].__tablename__}"
            self._merge(orm_objs, metric_label=metric_label)
        else:
            self._logger.warning("Merged empty batch.")

    @time_metric_wrapper(metric=TimeMetrics.SQLALCHEMY)
    def _execute(self, statement, session: Session = None, close_session=True, is_raw=False, **kwargs) -> List[
        Row[Any]]:
        s = session or self.session
        try:
            result = s.execute(statement)

            if close_session:
                s.commit()

            if is_raw:
                return list(result)
            else:
                return list(result.scalars())

        except ResourceClosedError:
            pass

        finally:
            if close_session:
                s.close()

    @time_metric_wrapper(metric=TimeMetrics.SQLALCHEMY)
    def _add(self, obj, session: Session = None, close_session=True, **kwargs):
        s = session or self.session
        try:
            s.add(obj)
            if close_session:
                s.commit()
        finally:
            if close_session:
                s.close()

    @time_metric_wrapper(metric=TimeMetrics.SQLALCHEMY)
    def _delete(self, obj, session: Session = None, close_session=True, **kwargs):
        s = session or self.session
        try:
            s.delete(obj)
            if close_session:
                s.commit()
        finally:
            if close_session:
                s.close()

    @time_metric_wrapper(metric=TimeMetrics.SQLALCHEMY)
    def _merge(self, objs: List[BaseORM], **kwargs):
        with self.session as s:
            PostgresMergeStrategy(objs, s).merge()
            s.commit()
