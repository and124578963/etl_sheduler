from . import *

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
    achive_id = db.Column(db.Integer, db.ForeignKey(f"{str(Schema.ARCHIVE)}.achievements.id"))
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

    get_dttm = db.Column(db.DateTime)
    lost_dttm = db.Column(db.DateTime, onupdate=func.now(), server_default=func.now())


class Comments_ARCH(BaseORM):
    __tablename__ = "comments_arch"
    __table_args__ = {"schema": str(Schema.ARCHIVE)}

    issue_id = db.Column(db.Integer, primary_key=True, nullable=False)
    date = db.Column(db.DateTime)
    name = db.Column(db.String)
    comment = db.Column(db.String)
    insert_dttm = db.Column(db.DateTime)
    archive_dttm = db.Column(db.DateTime)


class Issue_ARCH(BaseORM):
    __tablename__ = "issue_arch"
    __table_args__ = {"schema": str(Schema.ARCHIVE)}

    issue_id = db.Column(db.Integer, primary_key=True, nullable=False)
    issue_key = db.Column(db.String)
    summary = db.Column(db.String)
    description = db.Column(db.String)
    parent_id = db.Column(db.Integer)
    issue_type = db.Column(db.String)
    status = db.Column(db.String)
    project_key = db.Column(db.String)
    priority = db.Column(db.String)
    resolution = db.Column(db.String)
    id_assigne = db.Column(db.String)
    id_reporter = db.Column(db.String)
    creator = db.Column(db.String)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    resolved = db.Column(db.DateTime)
    affects_version = db.Column(db.String)
    fix_version = db.Column(db.String)
    due_date = db.Column(db.DateTime)
    security_level = db.Column(db.String)
    c_priority = db.Column(db.String)
    c_ext_system = db.Column(db.String)
    c_status = db.Column(db.String)
    time_response = db.Column(db.Float)
    time_resolution = db.Column(db.Float)
    insert_dttm = db.Column(db.DateTime)

    archive_dttm = db.Column(db.DateTime)


class Projects_ARCH(BaseORM):
    __tablename__ = "projects_arch"
    __table_args__ = {"schema": str(Schema.ARCHIVE)}

    project_key = db.Column(db.String, primary_key=True, nullable=False)
    project_name = db.Column(db.String)
    project_type = db.Column(db.String)
    project_lead = db.Column(db.String)
    project_description = db.Column(db.String)
    project_url = db.Column(db.String)

    archive_dttm = db.Column(db.DateTime)


class Score_ARCH(BaseORM):
    __tablename__ = "score_arch"
    __table_args__ = {"schema": str(Schema.ARCHIVE)}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer)
    amount_exp = db.Column(db.Integer)
    amount_cost = db.Column(db.Integer)

    archive_dttm = db.Column(db.DateTime)
