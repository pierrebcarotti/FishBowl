import pytest

from fish_bowl.process.topology import SquareGridCoordinate, TopologyError, square_grid_valid, square_grid_neighbours


class TestTopology:

    def test_square_grid_coordinate(self):
        coord = SquareGridCoordinate(1, 2)
        assert coord.x == 1
        assert coord.y == 2
        moved = coord.move(1, 1)
        assert moved.x == 2
        assert moved.y == 3

        coord_2 = SquareGridCoordinate(1, 3)
        coord_3 = SquareGridCoordinate(1, 2)
        assert not coord == coord_2
        assert coord == coord_3

    def test_valid_coordinate(self):
        assert square_grid_valid(10, SquareGridCoordinate(1, 2))
        # raise if invalid
        with pytest.raises(TopologyError):
            square_grid_valid(10, SquareGridCoordinate(10, 2))
        # invalid not raised
        assert not square_grid_valid(10, SquareGridCoordinate(-1, 2), raise_err=False)
        assert not square_grid_valid(10, SquareGridCoordinate(1, -1), raise_err=False)
        assert not square_grid_valid(10, SquareGridCoordinate(1, 10), raise_err=False)

    def test_neighbour_function(self):
        # full neighborhood
        neigh_list = square_grid_neighbours(10, SquareGridCoordinate(1, 1))
        assert len(neigh_list) == 8
        # corner
        neigh_list = square_grid_neighbours(10, SquareGridCoordinate(9, 9))
        assert len(neigh_list) == 3
        # line
        neigh_list = square_grid_neighbours(10, SquareGridCoordinate(0, 5))
        assert len(neigh_list) == 5
