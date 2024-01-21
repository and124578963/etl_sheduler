from enum import Enum

import sqlalchemy as db
from sqlalchemy import func
from sqlalchemy.orm import declarative_base, relationship

# Создаем базовый класс для объявления моделей данных
BaseORM = declarative_base()


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

