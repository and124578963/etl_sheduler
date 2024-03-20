from prometheus_client import start_http_server

from common.config_controller import Config
from time import sleep
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from scheduler.scheduler import Scheduler


if __name__ == "__main__":
    conf = Config()
    start_http_server(conf.data["prometheus"]["nodeExporterPort"])

    logger = Config.get_logger("scheduler")
    logger.info("Start application")

    cron_config = conf.data["cron"]
    actual_time = cron_config["job_actual_time"]
    first_execute_all = cron_config["first_execute_all"]

    scheduler_configs = {
        "job_defaults": {"misfire_grace_time": actual_time},
        "executors": {
            "default": ThreadPoolExecutor(1),
            "processpool": ProcessPoolExecutor(1),
        },
    }
    Scheduler(scheduler_configs).start()

    if first_execute_all:
        logger.info(
            "cron.first_execute_all is True: Все задачи отработали. Завершаем работу."
        )
        exit(0)

    while True:
        sleep(1)
