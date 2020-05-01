import json
import logging
import os
from typing import List, Dict

_logger = logging.getLogger(__name__)

# configuration files are located in simulation/configuration
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../configuration'))


def read_simulation_config(config_name: str) -> Dict:
    """
    Read a simulation .json configuration
    :param config_name:
    :return:
    """
    config_file = os.path.join(CONFIG_DIR, '{}.json'.format(config_name))
    with open(config_file, 'r') as fp:
        _logger.info('Reading simulation config from: {}'.format(config_file))
        return json.load(fp)


def save_simulation_config(config: Dict, config_name: str, overwrite: bool = False):
    """
    Persist a simulation configuration to file. Overwrite flag set to true will overwrite existing configuration
    :param config_name:
    :param overwrite:
    :return:
    """
    config_file = os.path.join(CONFIG_DIR, '{}.json'.format(config_name))
    if os.path.isfile(config_file) and not overwrite:
        raise FileExistsError('Configuration file with name={} already exists. Set overwrite flag to True'
                              .format(config_name))
    with open(config_file, 'w') as fp:
        json.dump(config, fp)
        _logger.info('Saved simulation config to: {}'.format(config_file))
    return

