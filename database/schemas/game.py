from ._common import *

"""
    Таблицы витрины геймификации
"""


class Achievements(BaseORM):
    __tablename__ = "achievements"
    __table_args__ = {"schema": str(Schema.GAME)}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)
    personal = db.Column(db.Boolean)
    group = db.Column(db.Boolean)
    cost = db.Column(db.Integer)
    goal = db.Column(db.Integer)
    offset = db.Column(db.Integer)
    type = db.Column(db.String)
    subtype = db.Column(db.String)
    frequency = db.Column(db.String)
    sql = db.Column(db.String)
    exp = db.Column(db.Integer)
    priority = db.Column(db.Integer)
