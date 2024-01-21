import logging
from datetime import timedelta, datetime, date
from enum import Enum
from typing import List
from sqlalchemy.orm import Session

from configs.config_controller import Config
from database.dao.gamification import Achievements, Score
from database.dao.jira import JiraUser
from database.dao.service import UploadHealthCheck
from database.db_connection import InternalDB

from scheduler.tasks.task_exceptions import NotActualDBData

class Task:
    critical_etl_names = []

    def __init__(self, name, interval):
        self.name = name
        self.interval_type = IntervalType.init(interval)
        self.cron = self.interval_type.cron
        self.db = InternalDB()
        self.transaction_session: Session = self.db.session
        self.score_helper = ScoreAndCostHelper(self.transaction_session)
        self.config = Config()
        self.cron_config = self.config.data["cron"]
        self.log = self.config.get_logger("scheduler")

    def run(self):
        self.log.info(f"Запуск таска '{self.name}'")
        try:
            self.apply()
            self.write_health_check("Done")
            self.log.info(f"Таск '{self.name}' успешно отработал!")

        except Exception as e:
            self.write_health_check("ERROR", error_text=str(e))
            self.log.error(
                    f"Таск '{self.name}' завершился с ошибкой! {str(e)}", exc_info=e
            )

    def write_health_check(self, status: str, error_text=""):
        hch = UploadHealthCheck(
                upload_dttm=datetime.now(),
                module_name=self.name,
                status=status,
                error_text=error_text,
        )
        self.db.insert_orm_obj(hch)

    def set_benefits(
            self, user: JiraUser, achievement: Achievements, amount_result: int
    ):
        self.score_helper.add_exp_to_user(user, amount_result, achievement.exp)
        self.score_helper.add_cost_to_user(user, achievement.cost)

    def commit_transaction(self):
        self.transaction_session.commit()
        self.transaction_session.close()

    def check_status_critical_etl(self):
        if len(self.critical_etl_names) == 0:
            return
        date_yesterday = f"'{date.today() - timedelta(days=1)}'::date"

        list_conditions = []
        for name in self.critical_etl_names:
            list_conditions.append(
                    f"( module_name = '{name}' and "
                    f"upload_dttm::date >= {date_yesterday}"
                    f")"
            )
        conditions = " OR ".join(list_conditions)

        sql = f"""select status from v_last_health_check where {conditions} """
        results = self.db.execute_raw_sql(sql)
        self.log.debug(f"Statement {sql} return {results} ")

        is_actual = False
        if len(results) == len(self.critical_etl_names):
            is_actual = all(map(lambda x: x[0] == "Done", results))

        if not is_actual:
            raise NotActualDBData(self.name)

    def apply(self):
        raise Exception("Этот класс - интерфейс")


class IntervalType(Enum):
    """
    Дни недели cron
    1 - вторник, 5 - суббота
    """

    EVERYDAY = ("Ежедневно", timedelta(days=1))
    WEEKLY = ("Еженедельно", timedelta(weeks=1))
    MONTHLY = ("Ежемесячно", timedelta(days=30))
    QUARTERLY = ("Ежеквартально", timedelta(days=91))
    YEARLY = ("Ежегодно", timedelta(days=365))
    CRON = "Cron string like * * * * *"
    UNASSIGN = "Неизвестный интервал"

    def __new__(cls, _type, timedelta=None):
        obj = object.__new__(cls)
        obj._value_ = _type
        obj.cron = Config().data["cron"]["intervals"].get(_type, None)
        obj.timedelta = timedelta
        return obj

    @classmethod
    def init(cls, _type):
        return cls(str(_type).strip().capitalize())

    @classmethod
    def _missing_(cls, _type: str):
        if _type.count(" ") == 4:
            obj = cls("Cron string like * * * * *")
            obj.cron = _type
            # При указании интервала в виде крон строки timedelta не бесконечна
            obj.timedelta = timedelta(days=365 * 100)
            return obj
        else:
            return cls.UNASSIGN

    @classmethod
    def allowed_values(cls):
        return ", ".join([e.value for e in cls if e != cls.UNASSIGN])


class AchiveType(Enum):
    ROLLING = "Переходящая"
    NOROLLING = "Непереходящая"
    PERSONAL = "Персональная"
    PROGRESS = "Прогрессивная"

    UNASSIGN = "Неопределенная"

    @classmethod
    def init(cls, type):
        return cls(str(type).strip().capitalize())

    @classmethod
    def _missing_(cls, value):
        return cls.UNASSIGN

    @classmethod
    def allowed_values(cls):
        return ", ".join([e.value for e in cls if e != cls.UNASSIGN])


class ScoreAndCostHelper:
    def __init__(self, transaction_session):
        self.db = InternalDB()
        self.transaction_session = transaction_session
        self.log = logging.getLogger("scheduler")

    def add_cost_to_user(self, user: JiraUser, cost: int):
        self.log.debug(f"Добавляем пользователю {user.display_name} - cost: {cost}")
        cond = [Score.user_id == str(user.id)]
        values = {"amount_exp": Score.amount_cost + cost}
        self.db.update_orm(Score, values=values, conditions=cond)

    def add_exp_to_user(self, user: JiraUser, amount: int, exp_of_one: int):
        exp = amount * exp_of_one
        self.log.debug(f"Добавляем пользователю {user.display_name} - опыт: {exp}")
        cond = [Score.user_id == str(user.id)]
        values = {"amount_exp": Score.amount_exp + exp}
        self.db.update_orm(Score, values=values, conditions=cond)

    def create_if_not_exist_score(self, list_user_id: List[str]):
        list_exist_user_id = self.db.select_orm(Score)
        for user_id in list_user_id:
            if user_id not in list_exist_user_id:
                self.init_score(user_id)

    def init_score(self, user_id: str):
        self.log.debug(f"Инициализируем Score для user_id: {user_id}")
        self.db.insert_orm_obj(Score(user_id=user_id, amount_cost=0, amount_exp=0))


class SQLAchieveResult:
    def __init__(self, user_id: str, amount: str):
        self.__db = InternalDB()
        self.user: JiraUser = self.__db.select_orm(
                JiraUser, conditions=[JiraUser.id == str(user_id)]
        )[0]
        self.amount: int = int(amount)

    def __str__(self):
        return f"{self.user.user_name} - {self.amount}"
