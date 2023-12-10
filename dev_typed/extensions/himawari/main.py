

import sys
import asyncio
import pendulum as pdl

from config import init_config
from query import query, FTP_HOST


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
    config.from_ini(config_file)
    input_file = config.get('file', 'input')
    output_file = config.get('file', 'output')
    mistiming = config.get('setting', 'mistiming')
    timezone = config.get('setting', 'timezone')
    num_length = config.get('setting', 'num_length')
    if output_file == '':
        output_file = pdl.now().strftime('%Y-%d-%m_%H-%M-%S.txt')
    timezone = pdl.local_timezone() if timezone == 'local' else pdl.UTC
    print('Time Zone:', timezone.name)

    with open(output_file, 'wt', encoding='utf-8') as out_f:
        for count, line in read_file(input_file):
            print(f'[%0{num_length}d]' % count)
            try:
                t1 = pdl.parse(line, tz=timezone)
                print(f'{line} >> {t1}')
            except:
                print(f'{line} >> 解析日期失败')
                continue

            success, result = asyncio.run(query(t1, mistiming))
            if success:
                out_f.write(f'ftp://{FTP_HOST}{result}\n')
                print(result)
            else:
                print('no match')
            print('')

if __name__ == '__main__':

    main(*sys.argv[1:])
