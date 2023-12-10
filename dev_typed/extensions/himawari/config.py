

from typed import *


def init_config():
    config = Config()
    config.add_section('file')
    config.add_option('file', 'input', Var(String, 'input.txt', desc='输入文件（为空时默认为input.txt）'))
    config.add_option('file', 'output', Var(String, desc='输出文件（为空时默认根据当地时间命名为%Y-%d-%m_%H-%M-%S.txt）'))
    config.add_section('setting')
    config.add_option('setting', 'mistiming', Var(Int, 600, desc='最大查询时间差（单位秒，为空时默认为600）'))
    config.add_option('setting', 'timezone', ComboVar(String, ['local', 'utc'], 'local', desc='输入时间时区（为空时默认为当地时区）'))
    config.add_option('setting', 'num_length', Var(Int, 4, desc='显示序号长度（为空时默认为4）'))
    return config
