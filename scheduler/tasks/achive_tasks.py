import datetime
from typing import List, Tuple

from common.utils import override
from database.schemas.archive import LostAchivePerUser
from database.schemas.cube import User
from database.schemas.game import Achievements, AchivePerUser, ProgressAchivePerUser
from metrics.prometheus_metrics import time_metric_wrapper, TimeMetrics, status_metric_wrapper, StatusMetrics, \
    ErrorMetric

from scheduler.tasks.task_common import Task, SQLAchieveResult
from scheduler.tasks.task_exceptions import EmptyResult


class AchieveTask(Task):
    def __init__(self, achieve_id: int, name: str, cron: str):
        super().__init__(name, cron)
        self.achieve_id = achieve_id
        self.achieve: Achievements = self.get_achieve(achieve_id)

    @status_metric_wrapper(status_metric=StatusMetrics.ACHIEVE_STATUS, error_metric=ErrorMetric.ACHIEVE)
    @time_metric_wrapper(metric=TimeMetrics.ACHIEVE_TIME)
    def apply(self, **kwargs):
        self.achieve: Achievements = self.get_achieve(self.achieve_id)
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
        if len(result) > 0:
            if len(result[0]) != 2:
                raise ValueError("SQL достижения должна возвращать значения в формате (user_id, amount)")
            for user_id, amount in result:
                list_obj.append(SQLAchieveResult(user_id, amount))
            return list_obj
        else:
            raise EmptyResult(self.name)

    def get_achieve(self, achieve_id: int) -> Achievements:
        achieve_list = self.db.select_orm(
            Achievements, conditions=[Achievements.id == str(achieve_id)], session=self.transaction_session
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
            raise EmptyResult(self.name)
        return results

    def count_achive(self, list_result: List[SQLAchieveResult]) -> List[User]:
        max_amount = max([res.amount for res in list_result])
        list_user_with_max = [
            res.user for res in list_result if res.amount == max_amount
        ]
        return list_user_with_max

    def assign_achive(self, list_user: List[User]):
        raise Exception(
            "Этот класс - интерфейс. Необходимо переопределить функцию assign_achieve"
        )

    def add_exp_to_users(self, list_result: List[SQLAchieveResult]):
        for res in list_result:
            if res.amount > 0 and self.achieve.exp > 0:
                self.score_helper.add_exp_to_user(res.user, res.amount, self.achieve.exp, self.achieve.id)


class RollingAchive(AchieveTask):

    @override
    def assign_achive(self, list_user: List[User]):
        self.unassign_old_achieve()
        for user in list_user:
            self.score_helper.add_cost_to_user(user, self.achieve.cost, self.achieve.id)
            self.log.debug(
                f"Добавляем пользователю {user.login} - достижение: {self.achieve.name}"
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
            self.db.delete_orm_obj(exist_achive, session=self.transaction_session)
            self.log.debug(
                f"Пользователь user_id: {exist_achive.user.login} - "
                f"потерял переходящую ачивку: {exist_achive.achive.name}"
            )


class NoRollingAchive(AchieveTask):
    @override
    def assign_achive(self, list_user: List[User]):
        for user in list_user:
            owners_id = [i.user_id for i in self.achieve.achive_x_user]
            if user.id not in owners_id:
                self.log.info(
                    f"Добавляем достижение: {self.achieve.name} - для {user.login}"
                )
                self.db.insert_orm_obj(
                    AchivePerUser(user_id=user.id, achive_id=self.achieve.id)
                )
                self.score_helper.add_cost_to_user(user, self.achieve.cost, self.achieve.id)
            else:
                self.log.info(
                    f"У пользователя {user.login} уже есть достижение: {self.achieve.name}"
                )


class ProgressAchive(AchieveTask):
    @override
    def count_achive(self, list_result: List[SQLAchieveResult]) -> List[User]:
        list_progress_a_x_u: List[ProgressAchivePerUser] = self.achieve.progress_achive_x_user
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
                f"Пользователь {res.user.login} набрал {res.amount} из {self.achieve.goal} для "
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
        list_user: List[User],
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
    def assign_achive(self, list_user: List[User]):
        for user in list_user:
            self.score_helper.add_cost_to_user(user, self.achieve.cost, self.achieve.id)
            self.db.insert_orm_obj(
                AchivePerUser(user_id=user.id, achive_id=self.achieve.id)
            )
            self.log.info(
                f"Пользователь {user.login} достиг достижения {self.achieve.name}"
            )


