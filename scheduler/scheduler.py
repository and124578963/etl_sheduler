from typing import List
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

from common.config_controller import Config
from database.schemas.game import Achievements
from database.db_connection import PostgresDB

from scheduler.tasks.achive_tasks import RollingAchive, NoRollingAchive, ProgressAchive
from scheduler.tasks.etl_tasks import ETL_Task, CLASS_LINK
from scheduler.tasks.task_common import Task, AchiveType, IntervalType


class Scheduler(BackgroundScheduler):

    def __init__(self, internal_configs):
        super().__init__(**internal_configs)
        CLASS_LINK["Scheduler"] = self
        self.db = PostgresDB()
        self.db.create_if_not_exist_metadata()

        conf = Config()
        self.__first_execute_all = conf.data["cron"]["first_execute_all"]
        self.__execute_achieve_etl = conf.data["cron"]["execute_achieve_etl"]
        self.list_etl_configs = conf.data["cron"]["etl"]
        self._log = Config.get_logger("scheduler")

        if not self.__first_execute_all and self.__execute_achieve_etl:
            self.start_task_now(ETL_Task("ETL_GET_DATA_FROM_GTABLE", None, is_critical=False))

        self.init_tasks()

    def init_tasks(self):
        for task_etl in self.get_etl_tasks():
            self.init_scheduled_tasks(task_etl)

        if self.__execute_achieve_etl:
            for task_ach in self.get_achive_tasks():
                self.init_scheduled_tasks(task_ach)

    def reinit_tasks(self):
        self.remove_all_jobs()
        self._log.info(
            "Обновлены данные характеристик достижений. Инициализируем джобы по новым данным."
        )
        self.init_tasks()

    def get_etl_tasks(self) -> List[Task]:
        etl_tasks = []
        for etl in self.list_etl_configs:
            if etl["enabled"]:
                etl_tasks.append(ETL_Task(etl["name"], etl["cron"], etl["critical"]))

        return etl_tasks

    def get_achive_tasks(self) -> List[Task]:
        list_achieve_tasks = []
        achieve_tasks = self.db.select_orm(Achievements)
        for task in achieve_tasks:
            type = task.type
            name = task.name
            frequency = task.frequency

            if AchiveType.init(type) is AchiveType.PERSONAL:
                continue

            if AchiveType.init(type) is AchiveType.ROLLING:
                list_achieve_tasks.append(RollingAchive(task.id, name, frequency))

            elif AchiveType.init(type) is AchiveType.NOROLLING:
                list_achieve_tasks.append(NoRollingAchive(task.id, name, frequency))

            elif AchiveType.init(type) is AchiveType.PROGRESS:
                list_achieve_tasks.append(ProgressAchive(task.id, name, frequency))

            elif AchiveType.init(type) is AchiveType.UNASSIGN:
                self._log.error(
                    f"Ачивка {name} имеет неопределенный тип {type}. "
                    f"Доступные варианты: {AchiveType.allowed_values()}"
                )
            else:
                raise Exception("Класс AchiveType работает неверно!")

        return list_achieve_tasks

    def init_scheduled_tasks(self, task_obj: Task):
        self._log.debug(
            f"Инициализация таска '{task_obj.name}' по расписанию '{task_obj.cron}'..."
        )
        if task_obj.interval_type != IntervalType.UNASSIGN:
            if self.__first_execute_all:
                self.start_task_now(task_obj)
            else:
                self.add_job(
                    task_obj.run, trigger=CronTrigger.from_crontab(task_obj.cron)
                )
        else:
            self._log.error(
                f"Неверный интервал у таска'{task_obj.name}'. "
                f"Доступные значения: '{IntervalType.allowed_values()}'..."
            )

    def start_task_now(self, task_obj: Task):
        self._log.info(
            f"cron.first_execute_all is True:'{task_obj.name}' запущен сейчас."
        )
        task_obj.run()
