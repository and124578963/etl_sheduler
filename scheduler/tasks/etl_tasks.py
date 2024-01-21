import importlib
from typing import List

from database.dao.gamification import PersonalAchievements
from scheduler.tasks.task_common import Task

CLASS_LINK = {}


class ETL_Task(Task):
    def __init__(self, name, cron, is_critical):
        super().__init__(name, cron)
        self.etl_module_path = f"ETL.{self.name}.main"

        if is_critical:
            self.add_critical_name()

    def apply(self):
        etl_module = importlib.import_module(self.etl_module_path)
        etl_module.main()

        if self.name == "ETL_GET_DATA_FROM_GTABLE":
            if not self.cron_config["first_execute_all"]:
                CLASS_LINK["Scheduler"].reinit_tasks()
            PersonalAchieveEtlTask().run()

    def add_critical_name(self):
        if self.name not in self.critical_etl_names:
            self.critical_etl_names.append(self.name)


class PersonalAchieveEtlTask(Task):
    def __init__(self):
        super().__init__("PersonalAchiveEtlTask", "NoCron")

    def apply(self):
        achieve_list = self.get_new_personal_achieve()
        self.check_exist_score(achieve_list)
        for achive in achieve_list:
            self.assign(achive)
        self.commit_transaction()

    def get_new_personal_achieve(self) -> List[PersonalAchievements]:
        return self.db.select_orm(
                orm_class=PersonalAchievements,
                conditions=[PersonalAchievements.is_processed != True],
                session=self.transaction_session,
        )

    # TODO: наверно надо переписать на список id а не ачивок
    def check_exist_score(self, achieve_list):
        list_user_id = [ach.user.id for ach in achieve_list]
        self.score_helper.create_if_not_exist_score(list_user_id)

    def assign(self, achive: PersonalAchievements):
        self.set_benefits(achive.user, achive.achievement, 1)
        achive.is_processed = True
        self.db.update_orm_obj(achive, session=self.transaction_session)
        self.log.info(
                f"Персональная ачивка {achive.achievement_name} добавлена пользователю {achive.user.display_name}"
        )
