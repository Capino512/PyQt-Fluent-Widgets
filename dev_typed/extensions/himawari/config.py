

from typed import *


def init_config():
    config = Config()
    config.add_section('file')
    config.add_option('file', 'input', StringVar('input.txt', desc='输入文件（为空时默认为input.txt）'))
    config.add_option('file', 'output', StringVar(desc='输出文件（为空时默认根据当地时间命名为%Y-%d-%m_%H-%M-%S.txt）'))
    config.add_section('setting')
    config.add_option('setting', 'mistiming', IntVar(600, desc='最大查询时间差（单位秒，为空时默认为600）'))
    config.add_option('setting', 'timezone', ComboVar(String, ['local', 'utc'], 'local', desc='输入时间时区（为空时默认为当地时区）'))
    config.add_option('setting', 'num_length', IntVar(4, desc='显示序号长度（为空时默认为4）'))
    config.add_section('ftp')
    config.add_option('ftp', 'user', StringVar(desc='ftp user name'))
    config.add_option('ftp', 'password', PasswordVar(desc='ftp user password'))
    config.add_option('ftp', 'timeout', IntVar(60, desc='ftp timeout'))
    config.add_section('aria2')
    config.add_option('aria2', 'download', BoolVar(False, desc='add to aria2 for download'))
    config.add_option('aria2', 'host', StringVar('http://localhost', desc='aria2 host'))
    config.add_option('aria2', 'port', IntVar(6800, desc='aria2 port'))
    config.add_option('aria2', 'secret', PasswordVar(desc='aria2 secret'))
    config.add_option('aria2', 'timeout', IntVar(60, desc='aria2 timeout'))
    return config
