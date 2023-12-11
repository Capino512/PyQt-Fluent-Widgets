

import sys
import time

from pprint import pp
from config import init_config


def main(config_path='config.ini'):
    config = init_config()
    config.load_ini(config_path)
    pp(config)
    time.sleep(3)


if __name__ == '__main__':

    main(*sys.argv[1:])
