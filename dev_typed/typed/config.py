

import configparser

from collections import OrderedDict


__all__ = ['Config']


class Config(OrderedDict):

    def add_section(self, section):
        self[section] = OrderedDict()

    def add_option(self, section, option, value):
        self[section][option] = value

    def get_option(self, section, option):
        return self[section][option].get_value()

    def dump_ini(self, path):
        parser = configparser.ConfigParser(allow_no_value=True)
        parser.optionxform = str  # upper case
        for section, values in self.items():
            parser.add_section(section)
            for option, value in values.items():
                parser.set(section=section, option=f';{value.get_desc()}')
                parser.set(section=section, option=option, value=value.to_string())
        with open(path, 'wt', encoding='utf-8') as f:
            parser.write(f)

    def load_ini(self, path):
        parser = configparser.ConfigParser()
        parser.optionxform = str  # upper case
        parser.read(path, encoding='utf-8')
        for section, values in self.items():
            for option, value in values.items():
                _value = value(parser.get(section, option))
                value.set_value(_value)
