

from typed import *


def parse_module_config():
    config = Config()
    config.add_section('module')
    config.add_option('module', 'name', Var(String, desc='module name'))
    config.add_option('module', 'config', Var(String, 'config.ini', desc='config file (.ini) path'))
    config.add_option('module', 'execute', Var(String, desc='executive command'))
    return config


def parse_input_config(init_config, config_path, mode):
    config = init_config()
    if mode == 'w':
        config.dump_ini(config_path)
    else:
        config.load_ini(config_path)
    return config
