

from typed import *


def init_config():
    config = Config()
    config.add_section('xxx')
    config.add_option('xxx', 'aaa', Var(Int, 10, 'desc'))
    config.add_option('xxx', 'bbb', Var(Float, 1.5, 'desc'))
    config.add_option('xxx', 'ccc', Var(Bool, desc='desc'))
    config.add_option('xxx', 'DDD', Var(String, 'abc', 'desc'))
    config.add_option('xxx', 'eee', ArrayVar(Int, 5, [1] * 5, 'desc'))
    config.add_option('xxx', 'fff', ListVar([Int, Float, Bool, String], [1, 1.2, True, 'aaa'], 'desc'))
    config.add_option('xxx', 'ggg', ComboVar(String, ['a', 'b', 'c'], 'a', 'desc'))
    config.add_option('xxx', 'hhh', ComboVar(Int, [1, 2, 3], 1, 'desc'))
    config.add_option('xxx', 'iii', ComboVar(Bool, [True, False], True, 'desc'))
    config.add_section('yyy')
    config.add_option('yyy', 'aaa', Var(Int, desc='desc'))
    config.add_option('yyy', 'bbb', Var(Float, desc='desc'))
    config.add_option('yyy', 'ccc', Var(Bool, desc='desc'))
    config.add_option('yyy', 'ddd', Var(String, desc='desc'))
    config.add_option('yyy', 'eee', OpenTextFileVar(desc='desc', filters="Images (*.png *.jpg *.bmp)"))
    config.add_option('yyy', 'fff', SaveTextFileVar(desc='desc'))
    config.add_option('yyy', 'ggg', DirVar(desc='desc'))
    return config
