

import configparser


__all__ = ['Bool', 'Int', 'Float', 'String', 'Unset']


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
Unset = object()
