import logging
import os
from typing import List, Dict, Type, Any

import sqlalchemy as db
from sqlalchemy import select, update, text, Row, delete
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql.ddl import CreateSchema
from sqlalchemy.sql.elements import OperatorExpression
from sqlalchemy.sql.operators import add

from database.dao import BaseORM, Schema
from common.utils import singleton, T
from metrics.sqlalchemy_metrics.utils import start_track_pool_metrics, db_execute_metric_wrapper


@singleton
class InternalDB:
    def __init__(self):
        # TODO: исправить, инициализация 2 раза происходит
        print("init InternalDB")
        self._logger = logging.getLogger("internalDB")
        self._engine = self._get_engine(username=os.getenv('POSTGRES_USER'),
                                        password=os.getenv('POSTGRES_PASSWORD'),
                                        host=os.getenv('POSTGRES_HOST'),
                                        port=os.getenv('POSTGRES_PORT'),
                                        db_name=os.getenv('POSTGRES_DB'),
                                        )

        start_track_pool_metrics(self._engine, "gamification")
        self._create_if_not_exist_metadata()

    def _get_engine(self, username: str, password: str, host: str, port: str, db_name: str) -> db.Engine:
        db_url = f"postgresql://{username}:{password}@{host}:{port}/{db_name}"
        self._logger.debug(db_url.replace(password, "hidden"))
        return db.create_engine(db_url)

    def _create_if_not_exist_metadata(self):
        connection = self._engine.connect()
        for schema in Schema:
            if not self._engine.dialect.has_schema(connection, schema.value):
                connection.execute(CreateSchema(schema.value))
        connection.commit()
        connection.close()
        BaseORM.metadata.create_all(self._engine)

    @property
    def session(self) -> Session:
        return sessionmaker(bind=self._engine)()

    # теперь все ORM классы проверяются в авто тестах pytest
    # def check_tables(self, tables: tuple[BaseORM]):
    #     with self.session as s:
    #         for table in tables:
    #             self._logger.debug(f'Проверка соответствия таблицы и ORM "{table.__tablename__}"')
    #             s.query(table).one()

    def truncate_orm_table(self, table: BaseORM):
        self._execute(select(table).delete())
        self._logger.debug(f'Таблица {table.__tablename__} удалена.')

    def update_orm_obj(self, orm_obj: BaseORM, session: Session):
        is_temp_session = False
        if session is None:
            session = self.session
            is_temp_session = True

        self._execute(add(orm_obj), session=session, close_session=is_temp_session)
        self._logger.debug(f'Updated {orm_obj.__tablename__} values: {orm_obj.__dict__} ')

    def insert_orm_obj(self, orm_obj: BaseORM):
        self._execute(add(orm_obj))
        self._logger.debug(f'Inserted into {orm_obj.__tablename__} data: {orm_obj.__dict__} ')

    def delete_orm_obj(self, orm_obj: BaseORM):
        self._execute(delete(orm_obj))
        self._logger.debug(f'{orm_obj.__dict__} deleted from {orm_obj.__tablename__}')

    def select_orm(self, orm_class: Type[T], conditions: List[OperatorExpression] = None,
                   session: Session = None) -> List[T]:
        if conditions is None:
            conditions = []

        is_temp_session = False
        if session is None:
            session = self.session
            is_temp_session = True

        statement_builder = select(orm_class)
        for cond in conditions:
            statement_builder = statement_builder.where(cond)

        orm_objects: List[T] = [i for i in self._execute(statement_builder, session=session,
                                                         close_session=is_temp_session)]

        return orm_objects

    def update_orm(self, orm_class: Type[BaseORM], values: Dict[str, OperatorExpression],
                   conditions: List[OperatorExpression] = None):

        conditions = conditions or []

        statement_builder = update(orm_class)
        for cond in conditions:
            statement_builder = statement_builder.where(cond)

        statement_builder = statement_builder.values(**values)
        self._execute(statement_builder)

    def execute_raw_sql(self, sql: str) -> list[Row[Any]]:
        return self._execute(text(sql))

    @db_execute_metric_wrapper
    def _execute(self, statement, session: Session = None, close_session=True) -> List[Row[Any]]:
        s = session or self.session
        try:
            result = s.execute(statement)
            if close_session:
                s.commit()
            return list(result.scalars())

        finally:
            if close_session:
                s.close()
