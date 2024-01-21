from . import *


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


class PersonalAchievements(BaseORM):
    __tablename__ = "pers_achieve"
    __table_args__ = {"schema": str(Schema.GAME)}

    id = db.Column(db.Integer, primary_key=True, nullable=False)

    login = db.Column(db.String, db.ForeignKey(f"{str(Schema.JIRA)}.user.user_name"))
    user = relationship(
            "JiraUser",
            foreign_keys=[
                login,
            ],
            backref=__tablename__,
    )

    achievement_name = db.Column(db.String, db.ForeignKey(f"{str(Schema.GAME)}.achievements.name"))
    achievement = relationship(
            "Achievements",
            foreign_keys=[
                achievement_name,
            ],
            backref=__tablename__,
    )

    is_processed = db.Column(db.Boolean, default=False)
    update_dttm = db.Column(db.DateTime, onupdate=func.now(), server_default=func.now())



class Score(BaseORM):
    __tablename__ = "score"
    __table_args__ = {"schema": str(Schema.GAME)}

    id = db.Column(db.Integer, primary_key=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey(f"{str(Schema.JIRA)}.user.id"))

    user = relationship("JiraUser", foreign_keys=[user_id], backref="score")

    amount_exp = db.Column(db.Integer)
    amount_cost = db.Column(db.Integer)


class AchivePerUser(BaseORM):
    __tablename__ = "achive_x_user"
    __table_args__ = {"schema": str(Schema.GAME)}

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    achive_id = db.Column(db.Integer, db.ForeignKey(f"{str(Schema.GAME)}.achievements.id"))
    user_id = db.Column(db.Integer, db.ForeignKey(f"{str(Schema.JIRA)}.user.id"))
    achive = relationship(
            "Achievements",
            foreign_keys=[achive_id],
            backref=__tablename__,
    )
    user = relationship(
            "JiraUser",
            foreign_keys=[user_id],
            backref=__tablename__,
    )
    update_dttm = db.Column(db.DateTime, onupdate=func.now(), server_default=func.now())


class ProgressAchivePerUser(BaseORM):
    __tablename__ = "progress_achive_x_user"
    __table_args__ = {"schema": str(Schema.GAME)}

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    achive_id = db.Column(db.Integer, db.ForeignKey(f"{str(Schema.GAME)}.achievements.id"))
    user_id = db.Column(db.Integer, db.ForeignKey(f"{str(Schema.JIRA)}.user.id"))
    achive = relationship(
            "Achievements",
            foreign_keys=[achive_id],
            backref=__tablename__,
    )
    user = relationship(
            "JiraUser",
            foreign_keys=[user_id],
            backref=__tablename__,
    )
    update_dttm = db.Column(db.DateTime, onupdate=func.now(), server_default=func.now())
    last_result = db.Column(db.Integer)
    is_done = db.Column(db.Boolean)
