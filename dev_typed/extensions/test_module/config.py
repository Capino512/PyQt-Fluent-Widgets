

from typed import *


def init_config():
    config = Config()
    config.add_section('xxx')
    config.add_option('xxx', 'a', BoolVar(desc='desc'))
    config.add_option('xxx', 'b', IntVar(10, desc='desc'))
    config.add_option('xxx', 'c', FloatVar(1.5, desc='desc'))
    config.add_option('xxx', 'd', StringVar('abc', desc='desc'))
    config.add_option('xxx', 'e', ArrayVar(Int, 5, [1] * 5, desc='desc'))
    config.add_option('xxx', 'f', ListVar([Int, Float, Bool, String], [1, 1.2, True, 'aaa'], desc='desc'))
    config.add_option('xxx', 'g', ComboVar(Bool, [True, False], True, desc='desc'))
    config.add_option('xxx', 'h', ComboVar(Int, [1, 2, 3], 1, desc='desc'))
    config.add_option('xxx', 'i', ComboVar(Float, [1.2, 2.3, 3.4], 1.2, desc='desc'))
    config.add_option('xxx', 'j', ComboVar(String, ['a', 'b', 'c'], 'a', desc='desc'))
    config.add_option('xxx', 'k', OpenFileVar(desc='desc', filters="Images (*.png *.jpg *.bmp)"))
    config.add_option('xxx', 'l', SaveFileVar(desc='desc'))
    config.add_option('xxx', 'm', DirVar(desc='desc'))
    config.add_option('xxx', 'n', IntRangeVar(-10, 10, desc='desc'))
    config.add_option('xxx', 'o', FloatRangeVar(-10, 10, desc='desc'))
    config.add_option('xxx', 'p', PasswordVar(desc='desc'))
    return config
