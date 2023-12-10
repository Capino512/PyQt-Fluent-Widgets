

import sys
import time

from pprint import pp
from config import init_config


def main(config_path='config.ini'):
    config = init_config()
    config.from_ini(config_path)
    pp(config.data)
    time.sleep(3)


if __name__ == '__main__':

    main(*sys.argv[1:])
