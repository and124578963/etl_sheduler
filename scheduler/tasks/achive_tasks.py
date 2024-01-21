import datetime
from typing import List, Tuple

from common.utils import override
from database.dao.archive import LostAchivePerUser
from database.dao.gamification import Achievements, AchivePerUser, ProgressAchivePerUser
from database.dao.jira import JiraUser

from scheduler.tasks.task_common import Task, SQLAchieveResult


class AchieveTask(Task):
    def __init__(self, achieve_id: int, name: str, cron: str):
        super().__init__(name, cron)
        self.achieve: Achievements = self.get_achieve(achieve_id)

    def apply(self):
        self.check_status_critical_etl()
        raw_result_list = self.execute_sql()
        list_of_result_obj = self.convert_result_to_obj(raw_result_list)
        self.log.info(str(list_of_result_obj))

        self.check_exist_score(list_of_result_obj)
        list_user_with_max = self.count_achive(list_of_result_obj)
        self.assign_achive(list_user_with_max)
        self.add_exp_to_users(list_of_result_obj)

    def check_exist_score(self, result_list: List[SQLAchieveResult]):
        list_user_id = [res.user.id for res in result_list]
        self.score_helper.create_if_not_exist_score(list_user_id)

    def convert_result_to_obj(self, result: List[Tuple]) -> List[SQLAchieveResult]:
        list_obj = []
        for user_id, amount in result:
            list_obj.append(SQLAchieveResult(user_id, amount))
        return list_obj

    def get_achieve(self, achieve_id: int) -> Achievements:
        achieve_list = self.db.select_orm(
            Achievements, conditions=[Achievements.id == str(achieve_id)]
        )
        if len(achieve_list) != 1:
            raise Exception(
                f"achive_id must be unique but exist: {', '.join([i.name for i in achieve_list])}"
            )

        return achieve_list[0]

    def prepare_sql_stmt(self, sql_text: str) -> str:
        from_dttm = str(datetime.date.today() - self.interval_type.timedelta)
        from_dttm = f"'{from_dttm}'::date"
        sql_text = sql_text.replace("{{FROM_DTTM}}", from_dttm)
        self.log.info(f"{self.name} SQL: \n{sql_text}\n")
        return sql_text

    def execute_sql(self) -> List[Tuple]:
        sql_stmt = self.prepare_sql_stmt(self.achieve.sql)
        results = self.db.execute_raw_sql(sql_stmt)
        results.sort(key=lambda row: int(row[1]), reverse=True)
        if not results:
            raise Exception("Result is empty")
        return results

    def count_achive(self, list_result: List[SQLAchieveResult]) -> List[JiraUser]:
        max_amount = max([res.amount for res in list_result])
        list_user_with_max = [
            res.user for res in list_result if res.amount == max_amount
        ]
        return list_user_with_max

    def assign_achive(self, list_user: List[JiraUser]):
        raise Exception(
            "Этот класс - интерфейс. Необходимо переопределить функцию assign_achive"
        )

    def add_exp_to_users(self, list_result: List[SQLAchieveResult]):
        for res in list_result:
            self.score_helper.add_exp_to_user(res.user, res.amount, self.achieve.exp)


class RollingAchive(AchieveTask):

    @override
    def assign_achive(self, list_user: List[JiraUser]):
        self.unassign_old_achieve()
        for user in list_user:
            self.score_helper.add_cost_to_user(user, self.achieve.cost)
            self.log.debug(
                f"Добавляем пользователю {user.display_name} - достижение: {self.achieve.name}"
            )
            self.db.insert_orm_obj(
                AchivePerUser(user_id=user.id, achive_id=self.achieve.id)
            )

    def unassign_old_achieve(self):
        achive_x_user: List[AchivePerUser] = self.achieve.achive_x_user
        for exist_achive in achive_x_user:
            to_lost_achive = LostAchivePerUser(
                achive_id=exist_achive.achive_id,
                user_id=exist_achive.user_id,
                get_dttm=exist_achive.update_dttm,
            )
            self.db.insert_orm_obj(to_lost_achive)
            self.db.delete_orm_obj(exist_achive)
            self.log.debug(
                f"Пользователь user_id: {exist_achive.user.display_name} - "
                f"потерял переходящую ачивку: {exist_achive.achive.name}"
            )


class NoRollingAchive(AchieveTask):
    @override
    def assign_achive(self, list_user: List[JiraUser]):
        for user in list_user:
            owners_id = [i.user_id for i in self.achieve.achive_x_user]
            if user.id not in owners_id:
                self.log.info(
                    f"Добавляем достижение: {self.achieve.name} - для {user.display_name}"
                )
                self.db.insert_orm_obj(
                    AchivePerUser(user_id=user.id, achive_id=self.achieve.id)
                )
                self.score_helper.add_cost_to_user(user, self.achieve.cost)
            else:
                self.log.info(
                    f"У пользователя {user.display_name} уже есть достижение: {self.achieve.name}"
                )


class ProgressAchive(AchieveTask):
    @override
    def count_achive(self, list_result: List[SQLAchieveResult]) -> List[JiraUser]:
        list_progress_a_x_u: List[
            ProgressAchivePerUser
        ] = self.achieve.progress_achive_x_user
        all_users_in_result = [i.user for i in list_result]
        self.create_progress_if_not_exist(all_users_in_result, list_progress_a_x_u)

        list_user_for_assign = []
        for res in list_result:
            progress_of_user = self.db.select_orm(
                ProgressAchivePerUser,
                conditions=[
                    ProgressAchivePerUser.achive_id == self.achieve.id,
                    ProgressAchivePerUser.user_id == res.user.id,
                ],
            )[0]
            if progress_of_user.is_done:
                continue

            self.log.debug(
                f"Пользователь {res.user.display_name} набрал {res.amount} из {self.achieve.goal} для "
                f"достижения {self.achieve.name}"
            )

            old_amount = progress_of_user.last_result
            if res.amount > self.achieve.offset:
                actual_amount = res.amount - self.achieve.offset
                if old_amount > self.achieve.offset:
                    actual_amount -= old_amount - self.achieve.offset
                if res.amount >= self.achieve.goal:
                    actual_amount -= res.amount - self.achieve.goal
                    progress_of_user.is_done = True
                    list_user_for_assign.append(res.user)
            else:
                actual_amount = 0

            self.update_progress_of_user(progress_of_user, res.amount)
            res.amount = actual_amount

            return list_user_for_assign

    def update_progress_of_user(self, progress_obj: ProgressAchivePerUser, new_amount):
        progress_obj.last_result = new_amount
        self.db.update_orm_obj(progress_obj)

    def create_progress_if_not_exist(
        self,
        list_user: List[JiraUser],
        list_progress_a_x_u: List[ProgressAchivePerUser],
    ):
        list_owners = [i.user_id for i in list_progress_a_x_u]
        for user in list_user:
            if user.id not in list_owners:
                self.db.insert_orm_obj(
                    ProgressAchivePerUser(
                        user_id=user.id,
                        achive_id=self.achieve.id,
                        last_result=0,
                        is_done=False,
                    )
                )

    @override
    def assign_achive(self, list_user: List[JiraUser]):
        for user in list_user:
            self.score_helper.add_cost_to_user(user, self.achieve.cost)
            self.db.insert_orm_obj(
                AchivePerUser(user_id=user.id, achive_id=self.achieve.id)
            )
            self.log.info(
                f"Пользователь {user.display_name} достиг достижения {self.achieve.name}"
            )

    @override
    def add_exp_to_users(self, list_result: List[SQLAchieveResult]):
        for res in list_result:
            self.score_helper.add_exp_to_user(res.user, res.amount, self.achieve.exp)
