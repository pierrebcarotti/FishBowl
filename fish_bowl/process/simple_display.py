import numpy as np
import pandas as pd
from typing import List, Tuple


"""
Display a grid 0-grid-1 x 0 -grid-1
"""


def convert_df_to_position(animal_df: pd.DataFrame) -> List[Tuple[int, Tuple[int, int]]]:
    """
    Convert the dataframe extracted from db and convert to a list of tuples
    :param animal_df:
    :return:
    """
    pos_list = []
    for idx, row in animal_df.iterrows():
        pos_list.append((row.animal_type.value, (row.coord_x, row.coord_y)))
    return pos_list


def display_simple_grid(animal_df: pd.DataFrame, grid_size):
    """
    set the list of tuple (animal, position) into a numpy 2d array
    :param animal_df:
    :param grid_size:
    :return:
    """
    grid = np.zeros(shape=(grid_size, grid_size), dtype=np.int)
    for at, pos in convert_df_to_position(animal_df):
        grid[pos[0], pos[1]] = at
    return grid
