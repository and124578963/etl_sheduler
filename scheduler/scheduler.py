
from typing import List
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

from common.utils import singleton
from configs.config_controller import Config
from database.dao.gamification import Achievements
from database.db_connection import InternalDB

from scheduler.tasks.achive_tasks import RollingAchive, NoRollingAchive, ProgressAchive
from scheduler.tasks.etl_tasks import ETL_Task, CLASS_LINK
from scheduler.tasks.task_common import Task, AchiveType, IntervalType


@singleton
class Scheduler(BackgroundScheduler):

    def __init__(self, config):
        super().__init__(**config)
        CLASS_LINK["Scheduler"] = self
        self.db = InternalDB()
        conf = Config()
        self._cron_conf = conf.data["cron"]
        self._log = conf.get_logger("scheduler")
        self.init_tasks()

    def init_tasks(self):
        for task_etl in self.get_etl_tasks():
            self.init_scheduled_tasks(task_etl)

        if self._cron_conf["execute_achieve_etl"]:
            for task_ach in self.get_achive_tasks():
                self.init_scheduled_tasks(task_ach)

    def reinit_tasks(self):
        self.remove_all_jobs()
        self._log.info(
                "Обновлены данные характеристик достижений. Инициализируем джобы по новым данным."
        )
        self.init_tasks()

    def get_etl_tasks(self) -> List[Task]:
        list_etl_conf = self._cron_conf["etl"]
        etl_tasks = []
        for etl in list_etl_conf:
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
            if self._cron_conf["first_execute_all"]:
                self._log.info(
                        f"cron.first_execute_all is True:'{task_obj.name}' запущен сейчас."
                )
                task_obj.run()
            else:
                self.add_job(
                        task_obj.run, trigger=CronTrigger.from_crontab(task_obj.cron)
                )
        else:
            self._log.error(
                    f"Неверный интервал у таска'{task_obj.name}'. "
                    f"Доступные значения: '{IntervalType.allowed_values()}'..."
            )
