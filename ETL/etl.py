from abc import ABC, abstractmethod
from datetime import datetime

from common.config_controller import Config
from configs.jira_to_csv_config import (team_name, required_fields_for_issue,
                                        required_fields_for_clone, start_url_to_issues, start_url_to_clone)

from database.schemas.cube import User, UserTimelog, WorkCalendar
from database.db_connection import PostgresDB
from database.schemas.jira import (Comments, Issue, IssueXClone)
from common.utils import get_classes_from_module

from gspread import service_account
from gspread.exceptions import APIError
from urllib3.exceptions import NewConnectionError

from database.schemas.dict import *
import os


class ETL(ABC):
    def __init__(self):
        self.conf = Config()
        self.db = PostgresDB()
        self._log = Config.get_logger(f"etl.{self.__class__.__name__}")

    @abstractmethod
    def main(self) -> None: ...

