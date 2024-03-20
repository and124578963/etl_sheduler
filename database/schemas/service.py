from ._common import *

"""

Служебные таблицы

"""


class UploadHealthCheck(BaseORM):
    __tablename__ = "upload_health_check"
    __table_args__ = {"schema": str(Schema.SERVICE)}

    upload_dttm = db.Column(db.DateTime, primary_key=True)
    module_name = db.Column(db.String, primary_key=True)
    status = db.Column(db.String)
    error_text = db.Column(db.String)
    db.PrimaryKeyConstraint("upload_dttm", "module_name")
