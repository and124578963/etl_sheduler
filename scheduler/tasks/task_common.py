import logging
from datetime import timedelta, datetime, date
from enum import Enum
from typing import List
from sqlalchemy.orm import Session

from common.config_controller import Config
from database.schemas.cube import User
from database.schemas.game import Achievements, Score, TransactionHistory

from database.schemas.service import UploadHealthCheck
from database.db_connection import PostgresDB

from scheduler.tasks.task_exceptions import NotActualDBData


class Task:
    critical_etl_names = []

    def __init__(self, name, interval):
        self.name = name
        self.interval_type = IntervalType.init(interval)
        self.cron = self.interval_type.cron
        self.db = PostgresDB()
        self.config = Config()
        self.cron_config = self.config.data["cron"]
        self.log = Config.get_logger(f"scheduler.{self.__class__.__name__}")
        self.transaction_session: Session = None
        self.score_helper: ScoreAndCostHelper = None

    def run(self):
        self.log.info(f"Запуск таска '{self.name}'")
        try:
            self.update_db_session()
            self.apply(metric_label=self.name)
            self.transaction_session.commit()
            self.write_health_check("Done")
            self.log.info(f"Таск '{self.name}' успешно отработал!")

        except Exception as e:
            self.write_health_check("ERROR", error_text=str(e))
            self.transaction_session.rollback()
            self.log.error(
                    f"Таск '{self.name}' завершился с ошибкой! {str(e)}", exc_info=e
            )
        finally:
            self.transaction_session.close()

    def update_db_session(self):
        if self.transaction_session is not None:
            self.transaction_session.close()
        self.transaction_session = self.db.session
        self.score_helper = ScoreAndCostHelper(self.transaction_session)

    def write_health_check(self, status: str, error_text=""):
        hch = UploadHealthCheck(
                upload_dttm=datetime.now(),
                module_name=self.name,
                status=status,
                error_text=error_text,
        )
        self.db.insert_orm_obj(hch)

    def set_benefits(
            self, user: User, achievement: Achievements, amount_result: int
    ):
        self.score_helper.add_exp_to_user(user, amount_result, achievement.exp, achievement.id)
        self.score_helper.add_cost_to_user(user, achievement.cost, achievement.id)

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

        sql = f"""select status from service.v_last_health_check where {conditions} """
        results = self.db.execute_raw_sql(sql)[0]
        self.log.debug(f"Statement {sql} return {results} ")

        is_actual = False
        if len(results) == len(self.critical_etl_names):
            is_actual = all(map(lambda x: x == "Done", results))

        if not is_actual:
            raise NotActualDBData(self.name)

    def apply(self, *args, **kwargs):
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
            # При указании интервала в виде крон строки timedelta бесконечна
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
        self.db = PostgresDB()
        self.transaction_session = transaction_session
        self.log = logging.getLogger("scheduler")

    def add_cost_to_user(self, user: User, cost: int, achievement_id: int):
        self.log.debug(f"Добавляем пользователю {user.login} - cost: {cost}")
        cond = [Score.user_id == str(user.id)]
        values = {"amount_cost": Score.amount_cost + cost}
        self.db.update_orm(Score, values=values, conditions=cond)
        trh = TransactionHistory(
            user_id=str(user.id),
            achievement_id=achievement_id,
            inserted_dttm=datetime.now(),
            added_cost=cost
        )
        self.db.insert_orm_obj(trh)

    def add_exp_to_user(self, user: User, amount: int, exp_of_one: int, achievement_id: int):
        exp = amount * exp_of_one
        self.log.debug(f"Добавляем пользователю {user.login} - опыт: {exp} за {amount} 5 действий")
        cond = [Score.user_id == str(user.id)]
        values = {"amount_exp": Score.amount_exp + exp}
        self.db.update_orm(Score, values=values, conditions=cond)
        trh = TransactionHistory(
            user_id=str(user.id),
            achievement_id=achievement_id,
            inserted_dttm=datetime.now(),
            added_exp=exp
        )
        self.db.insert_orm_obj(trh)

    def create_if_not_exist_score(self, list_user_id: List[str]):
        list_exist_score = self.db.select_orm(Score)
        list_exist_user_id = [i.user_id for i in list_exist_score]
        for user_id in list_user_id:
            if user_id not in list_exist_user_id:
                self.init_score(user_id)

    def init_score(self, user_id: str):
        self.log.debug(f"Инициализируем Score для user_id: {user_id}")
        self.db.insert_orm_obj(Score(user_id=user_id, amount_cost=0, amount_exp=0))


class SQLAchieveResult:
    def __init__(self, user_id: str, amount: str):
        self.__db = PostgresDB()
        self.user: User = self.__db.select_orm(User, conditions=[User.id == str(user_id)])[0]
        self.amount: int = int(amount)

    def __str__(self):
        return f"{self.user.user_name} - {self.amount}"
