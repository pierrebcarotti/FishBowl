"""
Dfines the topology of the grid

check coordinates
look for neighbours

"""
from collections import namedtuple
from typing import List
import random

SQUARE_NEIGH = {
    'nw': (-1, -1),
    'n': (0, -1),
    'ne': (1, -1),
    'w': (-1, 0),
    'e': (1, 0),
    'sw': (-1, 1),
    's': (0, 1),
    'se': (1, 1)
}


class NonEmptyCoordinate(Exception):
    pass


class TopologyError(Exception):
    pass


class SquareGridCoordinate(namedtuple('SquareGridCoordinate', ['x', 'y'])):
    __slots__ = ()

    def move(self, x: int, y: int) -> 'simulation.process.topology.SquareGridCoordinate':
        return SquareGridCoordinate(x=self.x + x, y=self.y + y)

    def __repr__(self):
        return "<x= {:.>3}, y= {:.>3}>".format(self.x, self.y)

    def __eq__(self, other):
        if not isinstance(other, SquareGridCoordinate):
            raise TypeError('Con only compare two SquareGridCoordinate object')
        return (self.x == other.x) and (self.y == other.y)


def square_grid_valid(grid_size: int, coordinates: SquareGridCoordinate, raise_err: bool = True) -> bool:
    """
    Check coordinate are valid in a square grid, raise assertion error if not
    :param grid_size:
    :param coordinates:
    :param raise_err:
    :return:
    """
    err = []
    if coordinates.x < 0:
        err.append("x coordinate must be positive")
    if coordinates.y < 0:
        err.append("y coordinate must be positive")
    if coordinates.x >= grid_size:
        err.append("x coordinate must be less than grid_size -1 = {}".format(grid_size - 1))
    if coordinates.y >= grid_size:
        err.append("y coordinate must be less than grid_size -1 = {}".format(grid_size - 1))
    if len(err) > 0:
        if raise_err:
            raise TopologyError(', '.join(err))
        else:
            return False
    return True


def square_grid_neighbours(grid_size: int, coordinate: SquareGridCoordinate,
                           shuffle: bool = True) -> List[SquareGridCoordinate]:
    """
    for a given corrdinate, return all 8 neighbours
    :param grid_size:
    :param coordinate:
    :param shuffle:
    :return:
    """
    neigh = []
    for k, (x, y) in SQUARE_NEIGH.items():
        new_coord = coordinate.move(x, y)
        if square_grid_valid(grid_size=grid_size, coordinates=new_coord, raise_err=False):
            neigh.append(new_coord)
    if shuffle:
        random.shuffle(neigh)
    return neigh
