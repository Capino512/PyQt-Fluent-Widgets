

import sys
import time

from functools import partial


print = partial(print, flush=True)


def main():
    print('[Info] 开始')
    for i in range(100):
        if i == 25:
            print('[Info] 步骤1...')
        if i == 50:
            print('[Warning] 步骤2...')
        if i == 75:
            print('[Error] 步骤3...')
        time.sleep(0.1)
        print(f'[Progress] {i + 1}')
    print('[Info] 成功')
    # time.sleep(1)


if __name__ == '__main__':

    main()
    sys.exit(0)


# 进度内容以 [Progress] 开头, 数值范围0-100
# 输出信息以 [Info] 开头
# 警告信息以 [Warning] 开头
# 错误信息以 [Error] 开头
# print 输出内容按utf-8编码格式解码, 及时刷新缓存, 防止输出内容阻塞
# time.sleep(1) 可在结尾添加睡眠等待, 保证输出完毕
# sys.exit(0) 运行成功程序返回0, 其他值视为运行出错
