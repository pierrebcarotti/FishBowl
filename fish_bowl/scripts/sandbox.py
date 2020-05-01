import logging

from fish_bowl.dataio.persistence import SimulationClient, get_database_string, Animals
from fish_bowl.process.base import SimulationGrid
from fish_bowl.process.utils import Animal
from fish_bowl.common.config_reader import read_simulation_config, save_simulation_config
from fish_bowl.process.simple_display import display_simple_grid
from fish_bowl.process.topology import SquareGridCoordinate

_logger = logging.getLogger(__name__)

sim_config = {
    'grid_size': 10,
    'init_nb_fish': 50,
    'fish_breed_maturity': 3,
    'fish_breed_probability': 80,
    'fish_speed': 2,
    'init_nb_shark': 5,
    'shark_breed_maturity': 5,
    'shark_breed_probability': 100,
    'shark_speed': 4,
    'shark_starving': 4
}

animal_list = [
    (Animal.Fish, SquareGridCoordinate(x=1, y=3)),
    (Animal.Fish, SquareGridCoordinate(x=2, y=1)),
    (Animal.Fish, SquareGridCoordinate(x=3, y=2)),
    (Animal.Fish, SquareGridCoordinate(x=4, y=3)),
    (Animal.Fish, SquareGridCoordinate(x=5, y=4)),
    (Animal.Shark, SquareGridCoordinate(x=6, y=5)),
    (Animal.Shark, SquareGridCoordinate(x=6, y=6)),
    (Animal.Fish, SquareGridCoordinate(x=6, y=1)),
]

a_list = [
            (Animal.Fish, SquareGridCoordinate(x=1, y=1)),
            (Animal.Fish, SquareGridCoordinate(x=2, y=1)),
            (Animal.Fish, SquareGridCoordinate(x=3, y=1)),
            (Animal.Fish, SquareGridCoordinate(x=1, y=3)),
            (Animal.Fish, SquareGridCoordinate(x=3, y=2)),
            (Animal.Shark, SquareGridCoordinate(x=2, y=2))
        ]

sim_config_empty = {
    'grid_size': 10,
    'init_nb_fish': 0,
    'fish_breed_maturity': 3,
    'fish_breed_probability': 80,
    'fish_speed': 2,
    'init_nb_shark': 0,
    'shark_breed_maturity': 5,
    'shark_breed_probability': 100,
    'shark_speed': 4,
    'shark_starving': 4}

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d:%(message)s")
    # save_simulation_config(sim_config, 'simulation_config_1', overwrite=True)
    # sim_config = read_simulation_config('simulation_config_2')
    client = SimulationClient(get_database_string())
    # sid = client.init_simulation(**sim_config)
    grid = SimulationGrid(persistence=client, simulation_parameters=sim_config)
    # for t, c in a_list:
    #     client.init_animal(sim_id=grid._sid, current_turn=0, animal_type=t, coordinate=c)

    print(display_simple_grid(client.get_animals_df(grid._sid), grid_size=sim_config['grid_size']))
    for turn in range(100):
        _logger.info('Turn: {}'.format(grid._sim_turn))
        grid.play_turn()
        print(display_simple_grid(grid.get_simulation_grid_data(), grid.get_simulation_parameters().grid_size))
        # _ = input('press key')

