import logging

from fish_bowl.dataio.persistence import SimulationClient, get_database_string
from fish_bowl.common.config_reader import read_simulation_config, save_simulation_config

_logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d:%(message)s")
    client = SimulationClient(get_database_string())
    for config in ['simulation_config_1', 'simulation_config_2']:
        sim_config = read_simulation_config(config)
        client.init_simulation(**sim_config)

