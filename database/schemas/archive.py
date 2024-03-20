

from ._common import *

"""

Архивные таблицы

"""


class LostAchivePerUser(BaseORM):
    __tablename__ = "lost_achive_x_user"
    __table_args__ = {
        "schema": str(Schema.ARCHIVE),
        # "postgresql_partition_by": 'RANGE (lost_dttm)'
    }

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    achive_id = db.Column(db.Integer, db.ForeignKey(f"{str(Schema.GAME)}.achievements.id"))
    user_id = db.Column(db.Integer, db.ForeignKey(f"{str(Schema.CUBE)}.user.id"))

    achive = relationship(
            "Achievements",
            foreign_keys=[achive_id],
            backref=f"{str(Schema.ARCHIVE)}.{__tablename__}",
    )
    user = relationship(
            "User",
            foreign_keys=[user_id],
            backref=f"{str(Schema.ARCHIVE)}.{__tablename__}",
    )

    get_dttm = db.Column(db.DateTime)
    lost_dttm = db.Column(db.DateTime, onupdate=func.now(), server_default=func.now())
