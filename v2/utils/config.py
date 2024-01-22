

import os

from typed import *


def init_main_config():
    config = Config()
    config.add_section('main_win')
    config.add_option('main_win', 'title', String('Demo'))
    config.add_option('main_win', 'icon', String('asserts/logo.png'))
    config.add_option('main_win', 'win_width', Int(960))
    config.add_option('main_win', 'win_height', Int(640))
    config.add_section('module_list')
    config.add_option('module_list', 'min_width', Int(120))
    config.add_option('module_list', 'max_width', Int(160))
    config.add_section('module')
    config.add_option('module', 'min_width', Int(500))
    config.add_option('module', 'btn_width', Int(100))
    config.add_option('module', 'text_area_min_width', Int(120))
    config.add_option('module', 'text_area_max_width', Int(240))
    config.add_option('module', 'label_width', Int(100))
    config.add_option('module', 'label_height', Int(33))
    config.add_option('module', 'label_warning_color', String('rgba(255, 0, 0, 200)'))
    return config


def init_module_config():
    config = Config()
    config.add_section('module')
    config.add_option('module', 'name', String(desc='module name'))
    config.add_option('module', 'desc', String(desc='module description'))
    config.add_option('module', 'config', String('config.ini', desc='config file (.ini) path'))
    config.add_option('module', 'execute', String( desc='executive command'))
    return config


def load_config(init_config, config_path, skip_error=False):
    config = init_config()
    if os.path.exists(config_path):
        config.load_ini(config_path, skip_error=skip_error)
    else:
        config.dump_ini(config_path)
    return config
