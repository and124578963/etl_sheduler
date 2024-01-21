from . import *

"""

Таблицы выгрузки из Jira

"""


class JiraUser(BaseORM):
    __tablename__ = "user"
    __table_args__ = {"schema": str(Schema.JIRA)}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_name = db.Column(db.String, unique=True, nullable=False)
    display_name = db.Column(db.String, nullable=False)
    email_address = db.Column(db.String)
    pool_name = db.Column(db.String)
    sub_pool_name = db.Column(db.String)
    row_update_dttm = db.Column(
            db.DateTime, onupdate=func.now(), server_default=func.now()
    )

    def __repr__(self):
        return self.display_name


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


class Issue(BaseORM):
    __tablename__ = "issue"
    __table_args__ = {"schema": str(Schema.JIRA)}

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


class Projects(BaseORM):
    __tablename__ = "projects"
    __table_args__ = {"schema": str(Schema.JIRA)}

    project_key = db.Column(db.String, primary_key=True, nullable=False)
    project_name = db.Column(db.String)
    project_type = db.Column(db.String)
    project_lead = db.Column(db.String)
    project_description = db.Column(db.String)
    project_url = db.Column(db.String)


class IssueXClone(BaseORM):
    __tablename__ = "issue_x_clone"
    __table_args__ = {"schema": str(Schema.JIRA)}

    issue_key = db.Column(db.Integer, primary_key=True, nullable=False)
    clone_key = db.Column(db.String(50))
    updated = db.Column(db.DateTime)
    insert_dttm = db.Column(db.DateTime)
