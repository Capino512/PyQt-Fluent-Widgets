

import configparser

from collections import OrderedDict


__all__ = ['Int', 'Float', 'Bool', 'String', 'Var', 'ArrayVar', 'ListVar', 'ComboVar', 'Config', '_Unset']


class _Type:
    def __init__(self, name, from_string, to_string):
        self.name = name
        self.from_string = from_string
        self.to_string = to_string

    def __call__(self, value):
        return self.from_string(value)


def string2bool(value):
    # '1': True , 'yes': True, 'true': True  , 'on': True
    # '0': False, 'no': False, 'false': False, 'off': False
    if value.lower() not in configparser.ConfigParser.BOOLEAN_STATES:
        raise ValueError('Not a boolean: %s' % value)
    return configparser.ConfigParser.BOOLEAN_STATES[value.lower()]


def bool2string(value):
    return 'true' if value else 'false'


Int = _Type('Int', int, str)
Float = _Type('Float', float, str)  # inf -inf nan
Bool = _Type('Bool', string2bool, bool2string)
String = _Type('String', str, str)
_Unset = object()


class _Var:
    def __init__(self, default=_Unset, desc=None):
        self._default = default
        self._desc = '' if (desc is None) else f' # {desc}'
        self._value = _Unset

    def get_value(self):
        return self._default if self._value is _Unset else self._value

    def set_value(self, value):
        self._value = value

    def has_value(self):
        return self.get_value() is not _Unset

    def reset(self):
        self._value = _Unset

    def _get_desc(self):
        raise NotImplementedError

    def get_desc(self):
        return self._get_desc() + self._desc

    def _to_string(self):
        raise NotImplementedError

    def to_string(self):
        return '' if (self._default is _Unset and self._value is _Unset) else self._to_string()

    def _from_string(self, value):
        raise NotImplementedError

    def from_string(self, value):
        return self._default if (value == '' and self._default is not _Unset) else self._from_string(value)

    def __call__(self, value):
        return self.from_string(value)


class Var(_Var):
    def __init__(self, type_, default=_Unset, desc=None):
        super(Var, self).__init__(default, desc)
        self.type = type_

    def _get_desc(self):
        default = '' if (self._default is _Unset) else f' default: {self.type.to_string(self._default)}'
        return f'[{self.type.name}]{default}'

    def _to_string(self):
        return self.type.to_string(self.get_value())

    def _from_string(self, value):
        return self.type(value)


class ArrayVar(_Var):
    def __init__(self, type_, length=None, default=_Unset, desc=None):
        super(ArrayVar, self).__init__(default, desc)
        self.type = type_
        self.length = length
        assert length is None or default is _Unset or len(default) == length

    def _get_desc(self):
        return f'[{self.type.name}] × ?' if (self.length is None) else f'[{self.type.name}] × {self.length}'

    def _to_string(self):
        return ', '.join([self.type.to_string(value) for value in self.get_value()])

    def _from_string(self, values):
        values = values.split(',')
        assert self.length is None or len(values) == self.length
        return [self.type(value.strip()) for value in values]


class ListVar(_Var):
    def __init__(self, type_list, default=_Unset, desc=None):
        super(ListVar, self).__init__(default, desc)
        self.type_list = type_list
        assert default is _Unset or len(default) == len(type_list)

    def _get_desc(self):
        return '[%s]' % ', '.join([type_.name for type_ in self.type_list])

    def _to_string(self):
        return ', '.join([type_.to_string(value) for type_, value in zip(self.type_list, self.get_value())])

    def _from_string(self, values):
        values = values.split(',')
        assert len(values) == len(self.type_list)
        return [type_(value.strip()) for type_, value in zip(self.type_list, values)]


class ComboVar(_Var):
    def __init__(self, type_, values, default=_Unset, desc=None):
        super(ComboVar, self).__init__(default, desc)
        self.type = type_
        self.values = values
        self.values_as_string = [type_.to_string(value) for value in values]
        assert default is _Unset or default in values

    def _get_desc(self):
        return f'[{self.type.name}] (%s)' % ', '.join(self.values_as_string)

    def _to_string(self):
        return self.type.to_string(self.get_value())

    def _from_string(self, value):
        value = self.type(value)
        assert value in self.values
        return value


class Config:
    def __init__(self):
        self.data = OrderedDict()

    def add_section(self, section):
        self.data[section] = OrderedDict()

    def add_option(self, section, option, value):
        self.data[section][option] = value

    def get(self, section, option):
        return self.data[section][option].get_value()

    def to_ini(self, path):
        parser = configparser.ConfigParser(allow_no_value=True)
        parser.optionxform = str  # upper case
        for section, values in self.data.items():
            parser.add_section(section)
            for option, value in values.items():
                parser.set(section=section, option=f';{value.get_desc()}')
                parser.set(section=section, option=option, value=value.to_string())
        with open(path, 'wt', encoding='utf-8') as f:
            parser.write(f)

    def from_ini(self, path):
        parser = configparser.ConfigParser()
        parser.optionxform = str  # upper case
        parser.read(path, encoding='utf-8')
        config = OrderedDict()
        for section, values in self.data.items():
            config[section] = OrderedDict()
            for option, value in values.items():
                _value = value(parser.get(section, option))
                value.set_value(_value)
                config[section][option] = _value
        return config
