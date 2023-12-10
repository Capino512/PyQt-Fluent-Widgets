

import sys

from pprint import pp


# init_config = None


def main(config_path='config.ini'):
    # global init_config
    # if init_config is None:
    #     from .config import init_config

    config = init_config()
    config.from_ini(config_path)
    pp(config.data)


if __name__ == '__main__':

    from config import init_config

    main(*sys.argv[1:])
