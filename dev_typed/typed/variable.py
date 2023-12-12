

from .base import *


__all__ = ['Var', 'BoolVar', 'IntVar', 'FloatVar', 'StringVar', 'PasswordVar', 'ArrayVar', 'ListVar', 'ComboVar',
           'InputFileOrDir', 'OutputFileOrDir', 'TextFile', 'FileVar', 'DirVar',
           'InputFileVar', 'OutputFileVar', 'InputTextFileVar', 'OutputTextFileVar', 'InputDirVar', 'OutputDirVar',
           'RangeVar', 'IntRangeVar', 'FloatRangeVar']


class _Var:
    def __init__(self, default=Unset, *, desc=None):
        self._default = default
        self._desc = '' if (desc is None) else f' # {desc}'
        self._value = Unset

    def get_value(self):
        return self._default if self._value is Unset else self._value

    def set_value(self, value):
        self._value = value

    def has_value(self):
        return self.get_value() is not Unset

    def reset(self):
        self._value = Unset

    def _get_desc(self):
        raise NotImplementedError

    def get_desc(self):
        return self._get_desc() + self._desc

    def _to_string(self):
        raise NotImplementedError

    def to_string(self):
        return '' if (self._default is Unset and self._value is Unset) else self._to_string()

    def _from_string(self, value):
        raise NotImplementedError

    def from_string(self, value):
        return self._default if (value == '' and self._default is not Unset) else self._from_string(value)

    def validate(self, value):
        return True

    def __call__(self, value):
        return self.from_string(value)


# validate  # todo
# correct
class Var(_Var):
    def __init__(self, type_, default=Unset, *, desc=None):
        super(Var, self).__init__(default, desc=desc)
        self.type = type_

    def _get_desc(self):
        default = '' if (self._default is Unset) else f' default: {self.type.to_string(self._default)}'
        return f'[{self.type.name}]{default}'

    def _to_string(self):
        return self.type.to_string(self.get_value())

    def _from_string(self, value):
        return self.type(value)

    def validate(self, value):
        try:
            self.from_string(value)
            return True
        except:
            return False


class BoolVar(Var):
    def __init__(self, default=Unset, *, desc=None):
        super(BoolVar, self).__init__(Bool, default, desc=desc)


class NumberVar(Var):
    def __init__(self, type_, default=Unset, lower=None, upper=None, *, desc=None):
        super(NumberVar, self).__init__(type_, default, desc=desc)
        self.lower = lower
        self.upper = upper

    def validate(self, value):
        if super().validate(value):
            value = self(value)
            return (self.lower is None or value >= self.lower) and (self.upper is None or value <= self.upper)
        return False


class IntVar(NumberVar):
    def __init__(self, default=Unset, lower=None, upper=None, *, desc=None):
        super(IntVar, self).__init__(Int, default, lower, upper, desc=desc)


class FloatVar(NumberVar):
    def __init__(self, default=Unset, lower=None, upper=None, *, desc=None):
        super(FloatVar, self).__init__(Float, default, lower, upper, desc=desc)


class RangeVar(Var):
    def __init__(self, type_, lower, upper, default=Unset, value_display_width=60, *, desc=None):
        super(RangeVar, self).__init__(type_, default, desc=desc)
        self.lower = lower
        self.upper = upper
        self.value_display_width = value_display_width

    def validate(self, value):
        if super().validate(value):
            value = self(value)
            return (self.lower is None or value >= self.lower) and (self.upper is None or value <= self.upper)
        return False


class IntRangeVar(RangeVar):
    def __init__(self, lower, upper, default=Unset, value_display_width=60, *, desc=None):
        super(IntRangeVar, self).__init__(Int, lower, upper, default, value_display_width, desc=desc)


class FloatRangeVar(RangeVar):
    def __init__(self, lower, upper, default=Unset, steps=100, precision=2, value_display_width=60, desc=None):
        super(FloatRangeVar, self).__init__(Float, lower, upper, default, value_display_width, desc=desc)
        self.steps = steps
        self.precision = precision


class StringVar(Var):
    def __init__(self, default=Unset, *, desc=None):
        super(StringVar, self).__init__(String, default, desc=desc)


class PasswordVar(StringVar):
    pass


class ArrayVar(_Var):
    def __init__(self, type_, length=None, default=Unset, *, desc=None):
        super(ArrayVar, self).__init__(default, desc=desc)
        self.type = type_
        self.length = length
        assert length is None or default is Unset or len(default) == length

    def _get_desc(self):
        return f'[{self.type.name}] × ?' if (self.length is None) else f'[{self.type.name}] × {self.length}'

    def _to_string(self):
        return ', '.join([self.type.to_string(value) for value in self.get_value()])

    def _from_string(self, values):
        values = values.split(',')
        assert self.length is None or len(values) == self.length
        return [self.type(value.strip()) for value in values]


class ListVar(_Var):
    def __init__(self, type_list, default=Unset, *, desc=None):
        super(ListVar, self).__init__(default, desc=desc)
        self.type_list = type_list
        assert default is Unset or len(default) == len(type_list)

    def _get_desc(self):
        return '[%s]' % ', '.join([type_.name for type_ in self.type_list])

    def _to_string(self):
        return ', '.join([type_.to_string(value) for type_, value in zip(self.type_list, self.get_value())])

    def _from_string(self, values):
        values = values.split(',')
        assert len(values) == len(self.type_list)
        return [type_(value.strip()) for type_, value in zip(self.type_list, values)]


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
        return self.type.to_string(self.get_value())

    def _from_string(self, value):
        value = self.type(value)
        assert value in self.values
        return value


class FileVar(Var):
    def __init__(self, default=Unset, filters='', *, desc=None):
        super(FileVar, self).__init__(String, default, desc=desc)
        self.filters = filters

    def validate(self, value):
        return value != '' or (self._default is not Unset)


class DirVar(Var):
    def __init__(self, default=Unset, *, desc=None):
        super(DirVar, self).__init__(String, default, desc=desc)

    def validate(self, value):
        return value != '' or (self._default is not Unset)


class InputFileOrDir:
    pass


class OutputFileOrDir:
    pass


class TextFile:
    pass


class InputFileVar(FileVar, InputFileOrDir):
    pass


class OutputFileVar(FileVar, OutputFileOrDir):
    pass


class InputTextFileVar(InputFileVar, TextFile):
    pass


class OutputTextFileVar(OutputFileVar, TextFile):
    pass


class InputDirVar(DirVar, InputFileOrDir):
    pass


class OutputDirVar(DirVar, OutputFileOrDir):
    pass
