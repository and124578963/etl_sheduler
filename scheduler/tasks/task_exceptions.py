class NotActualDBData(Exception):
    def __init__(self, job_name):
        self.job_name = job_name

    def __str__(self):
        return f"Неактуальная витрина. Таск {self.job_name} отменяется."


class EmptyResult(Exception):
    def __init__(self, job_name):
        self.job_name = job_name

    def __str__(self):
        return f"SQL достижения {self.job_name} вернул пустой результат."
