import pytest
from simulation.process.utils import Animal, convert_str_enum_to_name


class TestEnum:
    def test_convert_enum(self):
        v = 'Animal.Fish'
        assert convert_str_enum_to_name(v) == 'Fish'
