

import configparser

from collections import OrderedDict


__all__ = ['Config']


class Config(OrderedDict):

    def add_section(self, section, **kwargs):
        self[section] = OrderedDict()
        self[f'__{section}'] = kwargs

    def add_option(self, section, option, var, **kwargs):
        self[section][option] = var
        self[section][f'__{option}'] = kwargs

    def get_option(self, section, option):
        return self[section][option].get_value()

    def dump_ini(self, path):
        parser = configparser.ConfigParser(allow_no_value=True)
        parser.optionxform = str  # upper case
        for section, options in self.items():
            if section.startswith('__'):
                continue
            parser.add_section(section)
            for option, var in options.items():
                if option.startswith('__'):
                    continue
                parser.set(section=section, option=f';{repr(var)}')
                parser.set(section=section, option=option, value=str(var))
        with open(path, 'wt', encoding='utf-8') as f:
            parser.write(f)

    def load_ini(self, path, skip_error=False):
        parser = configparser.ConfigParser()
        parser.optionxform = str  # upper case
        parser.read(path, encoding='utf-8')
        for section, options in self.items():
            if section.startswith('__'):
                continue
            for option, var in options.items():
                if option.startswith('__'):
                    continue
                value = parser.get(section, option)
                if var.validate(value):
                    var.set_value(var(value))
                else:
                    assert skip_error, f'fail to parse `{value}`, {section} / {option} / {repr(var)}'