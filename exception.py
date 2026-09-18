class NegativeValueException(Exception):  # Исключение, которое выбросим,
    pass                                  # если получено число меньше нуля


def set_robot_power(value):
    if value < 0:
        raise NegativeValueException('Введите число не меньше нуля!')

set_robot_power(-1)