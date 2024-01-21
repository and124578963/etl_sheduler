from dotenv import load_dotenv
from prometheus_client import start_http_server

# from ETL.ETL_GET_DATA_FROM_GTABLE.main import main as ETL_GET_DATA_FROM_GTABLE
from configs.config_controller import Config
import sys
from time import sleep
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from database.db_connection import InternalDB
from scheduler.scheduler import Scheduler


def logging_excepthook(excType, excValue, traceback):
    logger.error(
        "Logging an uncaught exception", exc_info=(excType, excValue, traceback)
    )


if __name__ == "__main__":
    sys.excepthook = logging_excepthook
    conf = Config()
    start_http_server(conf.data["prometheus"]["nodeExporterPort"])

    cron_config = conf.data["cron"]
    logger = conf.get_logger("scheduler")
    load_dotenv()

    logger.info("Start application")
    InternalDB()

    actual_time = cron_config["job_actual_time"]
    first_execute_all = cron_config["first_execute_all"]
    execute_achieve_etl = cron_config["execute_achieve_etl"]

    # if not first_execute_all and execute_achieve_etl:
    #     ETL_GET_DATA_FROM_GTABLE()

    scheduller_configs = {
        "job_defaults": {"misfire_grace_time": actual_time},
        "executors": {
            "default": ThreadPoolExecutor(1),
            "processpool": ProcessPoolExecutor(1),
        },
    }

    Scheduler(scheduller_configs).start()


    if first_execute_all:
        logger.info(
            "cron.first_execute_all is True: Все задачи отработали. Завершаем работу."
        )
        exit(0)

    while True:
        sleep(1)
