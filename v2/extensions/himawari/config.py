

from typed import *


def init_config():
    config = Config()
    config.add_section('file')
    config.add_option('file', 'input', File('input.txt', is_editable_text=True, desc='输入文件（为空时默认为input.txt）'))
    config.add_option('file', 'output', File('', is_input=False, is_editable_text=True, desc='输出文件（为空时默认根据当地时间命名为%Y-%d-%m_%H-%M-%S.txt）'))
    config.add_section('setting')
    config.add_option('setting', 'mistiming', Int(600, desc='最大查询时间差（单位秒，为空时默认为600）'))
    config.add_option('setting', 'timezone', Combo(StringType, ['local', 'utc'], 'local', desc='输入时间时区（为空时默认为当地时区）'))
    config.add_option('setting', 'num_length', Int(4, desc='显示序号长度（为空时默认为4）'), hidden=True)
    config.add_section('ftp')
    config.add_option('ftp', 'user', String(desc='ftp user name'))
    config.add_option('ftp', 'password', Password(desc='ftp user password'))
    config.add_option('ftp', 'timeout', Int(60, desc='ftp timeout'), hidden=True)
    config.add_section('aria2')
    config.add_option('aria2', 'download', Switch(False, desc='add to aria2 for download'))
    config.add_option('aria2', 'host', String('http://localhost', desc='aria2 host'))
    config.add_option('aria2', 'port', Int(6800, desc='aria2 port'))
    config.add_option('aria2', 'secret', Password(desc='aria2 secret'))
    config.add_option('aria2', 'timeout', Int(60, desc='aria2 timeout'), hidden=True)
    return config
