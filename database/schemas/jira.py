from ._common import *

"""

Таблицы выгрузки из Jira

"""


class Comments(BaseORM):
    __tablename__ = "comments"
    __table_args__ = {"schema": str(Schema.JIRA)}

    # TODO: Добавил id свое, т.к. "duplicate key value violates unique constraint" по issue_id.
    # Возможно стоит брать из джиры comment_id
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    issue_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime)
    name = db.Column(db.String)
    comment = db.Column(db.String)
    insert_dttm = db.Column(db.DateTime)
