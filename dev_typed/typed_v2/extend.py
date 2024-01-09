

from .vars import *
from ._types import *


__all__ = [
    'IntSlider', 'FloatSlider', 'Password', 'ComboVar',
    'InputFile', 'OutputFile', 'InPutTextFile', 'OutPutTextFile', 'InputDir', 'OutputDir',
]


class _Slider(_Number):
    def __init__(self, type_, lower, upper, default=Unset, *, desc=None):
        super(_Slider, self).__init__(type_, default, lower, upper, desc=desc)


class IntSlider(_Slider):
    def __init__(self, lower, upper, default=Unset, *, desc=None):
        super(IntSlider, self).__init__(_Int, lower, upper, default, desc=desc)


class FloatSlider(_Slider):
    def __init__(self, lower, upper, default=Unset, steps=100, precision=2, desc=None):
        super(FloatSlider, self).__init__(_Float, lower, upper, default, desc=desc)
        self.steps = steps
        self.precision = precision


class Password(String):
    pass


class ComboVar(_Var):
    def __init__(self, type_, values, default=Unset, *, desc=None):
        super(ComboVar, self).__init__(default, desc=desc)
        self.type = type_
        self.values = values
        self.values_as_string = [type_.to_string(value) for value in values]
        assert default is Unset or default in values

    def _get_desc(self):
        return f'[{self.type.name}] (%s)' % ', '.join(self.values_as_string)

    def _to_string(self):
        return self.type.to_string(self.value)

    def _from_string(self, value):
        return  self.type(value)


class _File(String):
    def __init__(self, default=Unset, filters='', *, desc=None):
        super(String, self).__init__(default, desc=desc)
        self.filters = filters

    def _from_string(self, value):
        assert value != '' or (self._default is not Unset)
        return super()._from_string(value)


class _Dir(String):
    def __init__(self, default=Unset, *, desc=None):
        super(_Dir, self).__init__(default, desc=desc)

    def _from_string(self, value):
        assert value != '' or (self._default is not Unset)
        return super()._from_string(value)


class InputFile(_File):
    pass


class OutputFile(_File):
    pass


class InPutTextFile(_File):
    pass


class OutPutTextFile(_File):
    pass


class InputDir(_Dir):
    pass


class OutputDir(_Dir):
    pass
