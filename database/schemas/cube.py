from sqlalchemy import Sequence

from ._common import *

"""

Таблицы выгрузки из Cube

"""


class User(BaseORM):
    __tablename__ = "user"
    __table_args__ = {"schema": str(Schema.CUBE)}
    id_sec = Sequence(__tablename__ + "_id_seq")

    id = db.Column(db.Integer, id_sec, server_default=id_sec.next_value(), nullable=False, unique=True)
    login = db.Column(db.String, primary_key=True, nullable=False)
    user_name = db.Column(db.String)
    res_manager_name = db.Column(db.String)
    curator_name = db.Column(db.String)
    job_title = db.Column(db.String)
    office = db.Column(db.String)
    status = db.Column(db.String)
    pool_name = db.Column(db.String)
    email = db.Column(db.String)
    row_update_dttm = db.Column(
            db.DateTime, onupdate=func.now(), server_default=func.now()
    )


