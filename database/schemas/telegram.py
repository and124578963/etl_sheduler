from ._common import *

"""

Таблицы для телеграм бота

"""


class TGBotHistory(BaseORM):
    __tablename__ = "tg_bot_history"
    __table_args__ = {"schema": str(Schema.TELEGRAM)}

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    last_execute = db.Column(db.DateTime)

