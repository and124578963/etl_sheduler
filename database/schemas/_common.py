from enum import Enum
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import relationship
import sqlalchemy as db
from sqlalchemy.orm import declarative_base


# Создаем базовый класс для объявления моделей данных
BaseORM = declarative_base()


# Можно разбить на классы обычных view и материализованных
class BaseView:
    instances: List = []

    def __init__(self, schema, name, select_sql, is_materialized=False, tablespace="pg_default", priority=0):
        self.schema = str(schema)
        self.name = name
        self.select_sql = select_sql
        self.tablespace = tablespace
        self.is_materialized = is_materialized
        self.priority = priority
        BaseView.instances.append(self)

    def get_sql(self):
        if self.is_materialized:
            return f'CREATE MATERIALIZED VIEW {self.schema}.{self.name} ' \
                   f'TABLESPACE {self.tablespace} ' \
                   f'AS {self.select_sql}' \
                   f'WITH DATA;'
        else:
            return f'CREATE OR REPLACE VIEW {self.schema}.{self.name} ' \
                   f'AS {self.select_sql}'

    def is_exist(self, engine: db.Engine):
        if self.is_materialized:
            return engine.dialect.has_table(engine.connect(), table_name=self.name, schema=self.schema)
        else:
            # CREATE OR REPLACE пересоздаст вью в случае модификации
            return False


class Schema(Enum):
    ARCHIVE = "archive"
    JIRA = "jira"
    GAME = "game"
    CUBE = "cube"
    DICT = "dict"
    SERVICE = "service"
    TELEGRAM = "telegram"

    def __str__(self):
        return self.value

