

from typed import *


def init_config():
    config = Config()
    config.add_section('xxx')

    i = 96
    def fn():
        nonlocal i
        i += 1
        return chr(i)

    config.add_option('xxx', fn(), Bool(desc='desc'))
    config.add_option('xxx', fn(), Int(10, desc='desc'))
    config.add_option('xxx', fn(), Float(1.5, desc='desc'))
    config.add_option('xxx', fn(), String('abc', desc='desc'))
    config.add_option('xxx', fn(), Password(desc='desc'))
    config.add_option('xxx', fn(), Array(IntType, 5, [1] * 5, desc='desc'))
    config.add_option('xxx', fn(), List([IntType, FloatType, BoolType, StringType], [1, 1.2, True, 'aaa'], desc='desc'))
    config.add_option('xxx', fn(), Combo(BoolType, [True, False], True, desc='desc'))
    config.add_option('xxx', fn(), Combo(IntType, [1, 2, 3], 1, desc='desc'))
    config.add_option('xxx', fn(), Combo(FloatType, [1.2, 2.3, 3.4], 1.2, desc='desc'))
    config.add_option('xxx', fn(), Combo(StringType, ['a', 'b', 'c'], 'a', desc='desc'))
    config.add_option('xxx', fn(), File(desc='desc', is_input=False, filters="Images (*.png *.jpg *.bmp)"))
    config.add_option('xxx', fn(), File(desc='desc', is_input=True, filters="Images (*.png *.jpg *.bmp)"))
    config.add_option('xxx', fn(), File(desc='desc', is_input=True, is_editable_text=True, filters="Text (*.txt)"))
    config.add_option('xxx', fn(), Dir(desc='desc'))
    config.add_option('xxx', fn(), IntSlider(-10, 10, desc='desc'))
    config.add_option('xxx', fn(), FloatSlider(-10, 10, desc='desc'))
    config.add_option('xxx', fn(), Check(desc='desc'))
    config.add_option('xxx', fn(), Check(True, desc='desc'))
    config.add_option('xxx', fn(), Switch(False, desc='desc'))
    config.add_option('xxx', fn(), Radio(IntType, [1, 2, 3], desc='desc'))

    return config
