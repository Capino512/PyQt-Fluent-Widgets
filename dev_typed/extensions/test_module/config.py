

from typed import *


def init_config():
    config = Config()
    config.add_section('xxx')
    config.add_option('xxx', 'a', BoolVar(desc='desc'))
    config.add_option('xxx', 'b', IntVar(10, desc='desc'))
    config.add_option('xxx', 'c', FloatVar(1.5, desc='desc'))
    config.add_option('xxx', 'd', StringVar('abc', desc='desc'))
    config.add_option('xxx', 'e', PasswordVar(desc='desc'))
    config.add_option('xxx', 'f', ArrayVar(Int, 5, [1] * 5, desc='desc'))
    config.add_option('xxx', 'h', ListVar([Int, Float, Bool, String], [1, 1.2, True, 'aaa'], desc='desc'))
    config.add_option('xxx', 'h', ComboVar(Bool, [True, False], True, desc='desc'))
    config.add_option('xxx', 'i', ComboVar(Int, [1, 2, 3], 1, desc='desc'))
    config.add_option('xxx', 'j', ComboVar(Float, [1.2, 2.3, 3.4], 1.2, desc='desc'))
    config.add_option('xxx', 'k', ComboVar(String, ['a', 'b', 'c'], 'a', desc='desc'))
    config.add_option('xxx', 'l', InputFileVar(desc='desc', filters="Images (*.png *.jpg *.bmp)"))
    config.add_option('xxx', 'm', OutputFileVar(desc='desc'))
    config.add_option('xxx', 'n', InputTextFileVar(desc='desc', filters="Images (*.png *.jpg *.bmp)"))
    config.add_option('xxx', 'o', OutputTextFileVar(desc='desc'))
    config.add_option('xxx', 'p', InputDirVar(desc='desc'))
    config.add_option('xxx', 'q', OutputDirVar(desc='desc'))
    config.add_option('xxx', 'r', IntRangeVar(-10, 10, desc='desc'))
    config.add_option('xxx', 's', FloatRangeVar(-10, 10, desc='desc'))

    return config
