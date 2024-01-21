import inspect
import sys
import pytest
from dotenv import load_dotenv

from database import dao
from database.db_connection import InternalDB


@pytest.fixture(scope="session")
def db_class():
    load_dotenv()
    return InternalDB()

@pytest.fixture(scope="session")
def list_orm_classes():
    list_orm_classes = []
    for name, file in inspect.getmembers(sys.modules["database.dao"]):
        # if name == "db_gamification_tables":
            for class_name, class_obj in inspect.getmembers(file):
                if inspect.isclass(class_obj) and class_obj.__bases__[0] == dao.BaseORM and class_name != "BaseORM":
                    list_orm_classes.append(class_obj)
                    print(class_name)
    return list_orm_classes



def test_connection(db_class):
    db_class.execute_raw_sql('SELECT * FROM pg_stat_activity')

def test_orm_structure(db_class, list_orm_classes):
    for orm_class in list_orm_classes:
        result = db_class.select_orm(orm_class)
        if len(result) > 0:
            one_object = result[0]
            print(str(one_object))



