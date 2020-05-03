import pytest
from fish_bowl.process.utils import convert_str_enum_to_name


class TestEnum:
    def test_convert_enum(self):
        v = 'Animal.Fish'
        assert convert_str_enum_to_name(v) == 'Fish'
