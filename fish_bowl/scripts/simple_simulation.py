import logging
import argparse
import time

from fish_bowl.dataio.persistence import SimulationClient, get_database_string
from fish_bowl.process.base import SimulationGrid
from fish_bowl.common.config_reader import read_simulation_config
from fish_bowl.process.simple_display import display_simple_grid

_logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d:%(message)s")
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument('--config_name', default='simulation_config_1',
                            help='Simulation configuration file name')
    cmd_parser.add_argument('--max_turn', default=100, type=int, help='Maximum number of turns for the simulation')
    cmd_parser.add_argument('--config_path', default=None, type=str,
                            help="""
                            Configuration file path. If specified, configuration file will be loaded from this path
                            """)
    args = cmd_parser.parse_args()
    if args.config_path is not None:
        raise NotImplementedError('Code for directing to an alternative configuration'
                                  ' repository has not been implemented yet')
    # Load simulation configuration
    sim_config = read_simulation_config(args.config_name)
    # Instantiate client
    client = SimulationClient(get_database_string())
    # display initial grid
    grid = SimulationGrid(persistence=client, simulation_parameters=sim_config)
    print(display_simple_grid(client.get_animals_df(grid._sid), grid_size=sim_config['grid_size']))
    for turn in range(args.max_turn):
        timer = time.time()
        grid.play_turn()
        print(''.join(['*'] * sim_config['grid_size'] * 2))
        print('Turn: {turn: ^{size}}'.format(turn=grid._sim_turn, size=sim_config['grid_size']))
        print()
        print(display_simple_grid(grid.get_simulation_grid_data(), sim_config['grid_size']))
        print()
        print('Turn duration: {:<3}s'.format(int(time.time()-timer)))
        print()
