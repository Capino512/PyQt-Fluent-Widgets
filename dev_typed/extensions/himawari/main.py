

import sys
import aria2p
import asyncio
import pendulum as pdl

from functools import partial
from config import init_config
from query import query, FTP_HOST


print = partial(print, flush=True)


def read_file(path):
    with open(path, 'rt', encoding='utf-8') as f:
        count = 0
        for line in f.readlines():
            line = line.strip()
            if line == '###':
                break
            elif len(line) == 0 or line.startswith('#'):
                continue
            count += 1
            yield count, line


def main(config_file='config.ini'):
    config = init_config()
    config.load_ini(config_file)
    input_file = config.get_option('file', 'input')
    output_file = config.get_option('file', 'output')
    mistiming = config.get_option('setting', 'mistiming')
    timezone = config.get_option('setting', 'timezone')
    num_length = config.get_option('setting', 'num_length')
    ftp_user = config.get_option('ftp', 'user')
    ftp_password = config.get_option('ftp', 'password')
    ftp_timeout = config.get_option('ftp', 'timeout')
    download = config.get_option('aria2', 'download')
    aria2_host = config.get_option('aria2', 'host')
    aria2_port = config.get_option('aria2', 'port')
    aria2_secret = config.get_option('aria2', 'secret')
    aria2_timeout = config.get_option('aria2', 'timeout')
    if download:
        aria2 = aria2p.API(
            aria2p.Client(
                host=aria2_host,
                port=aria2_port,
                secret=aria2_secret,
                timeout=aria2_timeout,
            )
        )

    if output_file == '':
        output_file = pdl.now().strftime('%Y-%d-%m_%H-%M-%S.txt')
    timezone = pdl.local_timezone() if timezone == 'local' else pdl.UTC
    print('Time Zone:', timezone.name)

    results = []
    with open(output_file, 'wt', encoding='utf-8') as out_f:
        for count, line in read_file(input_file):
            print(f'[%0{num_length}d]' % count)
            try:
                t1 = pdl.parse(line, tz=timezone)
                print(f'{line} >> {t1}')
            except:
                print(f'{line} >> 解析日期失败')
                continue

            success, result = asyncio.run(query(ftp_user, ftp_password, ftp_timeout, t1, mistiming))
            if success:
                out_f.write(f'ftp://{FTP_HOST}{result}\n')
                results.append(result)
                print(result)
            else:
                print('no match')
            print('')
    if download:
        for result in results:
            aria2.add(f'ftp://{ftp_user}:{ftp_password}@{FTP_HOST}{result}')


if __name__ == '__main__':

    main(*sys.argv[1:])

    # pyinstaller -F -c -p . -p  D:\project\python\01\PyQt-Fluent-Widgets\dev_typed main.py
