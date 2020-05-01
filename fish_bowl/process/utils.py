import enum


class ImpossibleAction(Exception):
    # Exception for impossible action
    pass

class EndOfSimulatioError(Exception):
    # Simulation terminates because of condition
        pass


class Animal(enum.Enum):
    Fish = 1
    Shark = 2


def convert_str_enum_to_name(v):
    try:
        return v.split('.')[1]
    except:
        return v
