import json
from typing import Dict, List, Tuple, Union, Generator
from nyx.utils import logger

def load_mission_parameters():
    """ 
    Load the config.json file into a dictionary & validate
    """
    with open("nyx/config.json") as config_file:
        config: Dict[str, Union[Dict, List]] = json.load(config_file)

    logger.info("read parameters:")
    logger.info(config)

    return config