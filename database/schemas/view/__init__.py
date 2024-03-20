from database.schemas import Schema

__all__ = [f"{i.value}_view" for i in Schema]

