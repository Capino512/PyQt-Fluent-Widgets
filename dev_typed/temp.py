import os.path

print(os.path.isfile('temp.pyx'))
print(os.path.isdir('d:/temp-dfg'))
import pathlib


# pathlib.Path().val

import importlib

# importlib.

import re

def is_valid_path(path):
    pattern = r'^[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*$'
    return re.match(pattern, path) is not None

# 检查路径格式
path = r"C:\Users\John\Desktop\file.txt"
path = r"C:/Users/John\Desktop\file.txt"

print(is_valid_path(path))


print(all([]))

for s in [
    '',
    '1',
    '10000',
    '-1',
    '-10000',
    '1.0',
    '-1.0',
    '1e8',
    '1e-8',
    '1.1e8',
    '1.1e-8',
]:
    print(s, s.isalnum(), s.isalpha(), s.isdigit(), s.isdecimal(), s.isnumeric())


print(os.path.isabs(''))
print(os.path.isabs('temp'))
print(os.path.isabs('d:/temp'))
print(os.path.isabs('/temp'))
