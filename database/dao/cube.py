from . import *

"""

Таблицы выгрузки из Jira Cube

"""


class Users(BaseORM):
    __tablename__ = "users"
    __table_args__ = {"schema": str(Schema.CUBE)}

    user_key = db.Column(db.String, primary_key=True, nullable=False)
    user_name = db.Column(db.String)
    lower_name = db.Column(db.String)
    res_manager_name = db.Column(db.String)
    curator_name = db.Column(db.String)
    job_title = db.Column(db.String)
    office = db.Column(db.String)
    status = db.Column(db.String)
    pool_name = db.Column(db.String)
    email = db.Column(db.String)


class UserTimelog(BaseORM):
    __tablename__ = "user_timelog"
    __table_args__ = {"schema": str(Schema.CUBE)}

    user_name = db.Column(db.String, primary_key=True, nullable=False)
    log_date = db.Column(db.Date, primary_key=True, nullable=False)
    issue_id = db.Column(db.String, primary_key=True, nullable=False)
    issue_summary = db.Column(db.String)
    project = db.Column(db.String)
    fin_project = db.Column(db.String)
    time_worked_days = db.Column(db.Float, primary_key=True, nullable=False)


class WorkCalendar(BaseORM):
    __tablename__ = "work_calendar"
    __table_args__ = {"schema": str(Schema.CUBE)}

    user_name = db.Column(db.String, primary_key=True, nullable=False)
    log_date = db.Column(db.Date, primary_key=True, nullable=False)
    sick_leave = db.Column(db.Float)
    day_off = db.Column(db.Float)
    vacation = db.Column(db.Float)
    working = db.Column(db.Float)
    total_wl = db.Column(db.Float)


