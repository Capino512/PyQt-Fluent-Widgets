

from ._types import *


__all__ = ['Bool', 'Int', 'Float', 'String', 'Array', 'List', '_Var', '_Number']


class _Var:
    def __init__(self, default=Unset, *, desc=None):
        self._default = default
        self._desc = '' if (desc is None) else f' # {desc}'
        self._value = Unset

    @property
    def value(self):
        return self._default if self._value is Unset else self._value

    @value.setter
    def value(self, value):
        self._value = value

    def reset(self):
        self._value = Unset

    def has_value(self):
        return self.value is not Unset

    def _get_desc(self):
        raise NotImplementedError

    @property
    def desc(self):
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
        try:
            self.from_string(value)
            return True
        except:
            return False

    def __call__(self, value):
        return self.from_string(value)

    def __repr__(self):
        return self.desc

    def __str__(self):
        return self.to_string()


class _SingleVar(_Var):
    def __init__(self, type_, default=Unset, *, desc=None):
        super(_SingleVar, self).__init__(default, desc=desc)
        self.type = type_

    def _get_desc(self):
        default = '' if (self._default is Unset) else f' default: {self.type.to_string(self._default)}'
        return f'[{self.type.name}]{default}'

    def _to_string(self):
        return self.type.to_string(self.value)

    def _from_string(self, value):
        return self.type(value)


class Bool(_SingleVar):
    def __init__(self, default=Unset, *, desc=None):
        super(Bool, self).__init__(_Bool, default, desc=desc)


class _Number(_SingleVar):
    def __init__(self, type_, default=Unset, minimum=None, maximum=None, clamp=False, check_range=True, *, desc=None):
        super(_Number, self).__init__(type_, default, desc=desc)
        self.minimum = minimum
        self.maximum = maximum
        self.clamp = clamp
        self.check_range = check_range

    def _from_string(self, value):
        value = super()._from_string(value)
        if self.clamp:
            if self.minimum is not None:
                value = max(value, self.minimum)
            if self.maximum is not None:
                value = max(value, self.minimum)
        elif self.check_range:
            assert (self.minimum is None or value >= self.minimum) and (self.maximum is None or value <= self.maximum)
        return value


class Int(_Number):
    def __init__(self, default=Unset, minimum=None, maximum=None, clamp=False, check_range=False, *, desc=None):
        super(Int, self).__init__(_Int, default, minimum, maximum, clamp, check_range, desc=desc)


class Float(_Number):
    def __init__(self, default=Unset, minimum=None, maximum=None, clamp=False, check_range=False, *, desc=None):
        super(Float, self).__init__(_Float, default, minimum, maximum, clamp, check_range, desc=desc)


class String(_SingleVar):
    def __init__(self, default=Unset, *, desc=None):
        super(String, self).__init__(_String, default, desc=desc)


class Array(_Var):
    def __init__(self, type_, length=None, default=Unset, *, desc=None):
        super(Array, self).__init__(default, desc=desc)
        self.type = type_
        self.length = length
        assert length is None or default is Unset or len(default) == length

    def _get_desc(self):
        return '[{}] × {}'.format(self.type.name, '?' if self.length is None else self.length)

    def _to_string(self):
        return ', '.join([self.type.to_string(value) for value in self.value])

    def _from_string(self, values):
        values = values.split(',')
        assert self.length is None or len(values) == self.length
        return [self.type(value.strip()) for value in values]


class List(_Var):
    def __init__(self, type_list, default=Unset, *, desc=None):
        super(List, self).__init__(default, desc=desc)
        self.type_list = type_list
        assert default is Unset or len(default) == len(type_list)

    def _get_desc(self):
        return '[%s]' % ', '.join([type_.name for type_ in self.type_list])

    def _to_string(self):
        return ', '.join([type_.to_string(value) for type_, value in zip(self.type_list, self.value)])

    def _from_string(self, values):
        values = values.split(',')
        assert len(values) == len(self.type_list)
        return [type_(value.strip()) for type_, value in zip(self.type_list, values)]
