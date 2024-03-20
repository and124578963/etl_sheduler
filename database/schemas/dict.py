from ._common import *

"""

Словари

"""


class ProjectSla(BaseORM):
    __tablename__ = "project_sla"
    __table_args__ = {"schema": str(Schema.DICT)}

    project = db.Column(db.String, primary_key=True)
    priority = db.Column(db.String, primary_key=True)
    time_to_first_response = db.Column(db.Float)
    time_to_resolution = db.Column(db.Float)
    ext_system = db.Column(db.String, primary_key=True)
    service = db.Column(db.String, primary_key=True)

    db.PrimaryKeyConstraint("project", "priority", "ext_system", "service")
