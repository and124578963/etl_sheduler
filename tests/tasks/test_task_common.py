from typing import List, Tuple

import pytest

from scheduler.tasks.task_common import IntervalType, AchiveType


def generate_with_diferent_layout(list_input, list_output, to_list):
    for _input, _output in list(zip(list_input, list_output)):
        to_list.append((_input, _output))
        to_list.append((_input.lower(), _output))
        to_list.append((_input.upper(), _output))
        to_list.append((_input.capitalize(), _output))
        to_list.append((" " + _input + " ", _output))

class TestIntervalType:
    @pytest.fixture(scope="session")
    def generated_input_output(self) -> List[Tuple]:
        list_input_output = []

        list_normal_values = ["Ежедневно", "Еженедельно", "Ежемесячно",
                              "Ежеквартально", "Ежегодно"]
        list_result = [IntervalType.EVERYDAY, IntervalType.WEEKLY, IntervalType.MONTHLY,
                       IntervalType.QUARTERLY, IntervalType.YEARLY]

        generate_with_diferent_layout(list_normal_values, list_result, list_input_output)

        list_input_output.append(("asdasd", IntervalType.UNASSIGN))
        list_input_output.append(("", IntervalType.UNASSIGN))
        list_input_output.append((None, IntervalType.UNASSIGN))
        list_input_output.append((True, IntervalType.UNASSIGN))

        list_input_output.append(("* * * * *", IntervalType.CRON))
        list_input_output.append((" * * * * * ", IntervalType.CRON))
        list_input_output.append(("1 2 3 4 5", IntervalType.CRON))
        list_input_output.append(("12 12 13 14 15", IntervalType.CRON))

        return list_input_output

    def test_init(self, generated_input_output):
        for inp, outp in generated_input_output:
            interval_type = IntervalType.init(inp)
            assert interval_type is outp
            if interval_type is not IntervalType.UNASSIGN:
                assert interval_type.cron is not None
            else:
                assert interval_type.cron is None


class TestAchiveType:
    @pytest.fixture(scope="session")
    def generated_input_output(self) -> List[Tuple]:
        list_input_output = []

        list_normal_values = ["Переходящая", "Непереходящая", "Персональная",
                              "Прогрессивная"]
        list_result = [AchiveType.ROLLING, AchiveType.NOROLLING, AchiveType.PERSONAL,
                       AchiveType.PROGRESS]

        generate_with_diferent_layout(list_normal_values, list_result, list_input_output)

        list_input_output.append(("Неопределенная", AchiveType.UNASSIGN))
        list_input_output.append(("", AchiveType.UNASSIGN))
        list_input_output.append(("asdqwe", AchiveType.UNASSIGN))
        list_input_output.append((None, AchiveType.UNASSIGN))
        list_input_output.append((True, AchiveType.UNASSIGN))

        return list_input_output

    def test_init(self, generated_input_output):
        for i, o in generated_input_output:
            assert AchiveType.init(i) is o
