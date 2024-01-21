from logging import Logger
from yaml import load, Loader
import logging.handlers

from common.utils import singleton


@singleton
class Config:
    def __init__(self):
        with open("./application.yaml", "r", encoding="utf-8") as f:
            self.data = load(f, Loader)

        with open("./configs/mapper.yaml", "r", encoding="utf-8") as f:
            self.mapper = load(f, Loader)

        self._allowed_logger_names = []
        self._logging_init()

    def get_logger(self, logger_name: str) -> Logger:
        if logger_name not in self._allowed_logger_names:
            raise Exception(f"Логгер {logger_name} не задан в application.yaml")
        return logging.getLogger(logger_name)

    def _logging_init(self):
        # TODO: попробовать loguru
        log_path = self.data["logging"]["path"]
        backup_count = self.data["logging"]["backupCount"]
        max_megabytes = self.data["logging"]["maxMegaBytes"]
        loggers = self.data["logging"]["loggers"]

        logging.basicConfig(
                level=logging.ERROR,
                format="%(asctime)s [%(levelname)s] %(name)s - %(filename)s - %(funcName)s: %(message)s",
                handlers=[
                    logging.StreamHandler(),
                    logging.handlers.RotatingFileHandler(
                            filename=log_path,
                            maxBytes=max_megabytes * 1024,
                            backupCount=backup_count,
                            encoding="UTF-8",
                    ),
                ],
        )
        for logger in loggers:
            lvl = logging.getLevelName(logger["lvl"])
            logger_name = logger["name"]
            logging.getLogger(logger_name).setLevel(lvl)
            self._allowed_logger_names.append(logger_name)
