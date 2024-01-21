from abc import ABC, abstractmethod


# При наследовании от этого класса, он обязывает иметь функцию main в вашем классе, которая будет управляющей
class ETL(ABC):

    @abstractmethod
    def main(self) -> None: ...
