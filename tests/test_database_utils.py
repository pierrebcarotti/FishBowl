from simulation.dataio.database import blank_password


class TestDataBaseUtils:
    def test_blank_password(self):
        blanked = blank_password('blah://user:password@something')
        assert 'password' not in blanked
