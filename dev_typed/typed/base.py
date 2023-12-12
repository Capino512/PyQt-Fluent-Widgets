

import configparser


__all__ = ['Bool', 'Int', 'Float', 'String', 'Unset']


BOOLEAN_STATES = configparser.ConfigParser.BOOLEAN_STATES
# '1': True , 'yes': True, 'true': True  , 'on': True
# '0': False, 'no': False, 'false': False, 'off': False


class _Type:
    def __init__(self, name, from_string, to_string):
        self.name = name
        self.from_string = from_string
        self.to_string = to_string

    def __call__(self, value):
        return self.from_string(value)


def string2bool(value):
    assert value in BOOLEAN_STATES, 'Not a boolean: %s' % value
    return BOOLEAN_STATES[value.lower()]


def bool2string(value):
    return 'true' if value else 'false'


Int = _Type('Int', int, str)
Float = _Type('Float', float, str)  # inf -inf nan
Bool = _Type('Bool', string2bool, bool2string)
String = _Type('String', str, str)
Unset = object()
