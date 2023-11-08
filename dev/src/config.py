

import os
import pandas as pd
from pprint import pp


title = '冰冻圈关键要素模型模拟与反演平台'


# algos = [
#     dict(
#         id='id',
#         name='name',
#         description='description',
#         executable='executable',
#         outputs=[('name', 'postfix', 'flag')],
#     )
# ]
# 
# 
# # 1111 /模拟仿真子平台/积雪/模拟仿真/全球尺度
# # 112
# # 113
# 
# sub_funcs = [
#     dict(
#         name='全球尺度',
#         algos=algos,
#     )
# ]
# 
# 
# funcs = [
#     dict(
#         name='模拟仿真',
#         funcs=sub_funcs,
#     )
# ]
# 
# sub_modules = [
#     dict(
#         name='积雪',
#         funcs=funcs
#     )
# ]
# 
# 
# modules = [
#     dict(
#         name='模拟仿真子平台',
#         sub_modules=sub_modules
#     )
# ]

modules = []

def add_module(module):
    modules.append(
        dict(
            name=module,
            sub_modules=[]
        )
    )


def get_module(module):
    for _module in modules:
        if module == _module['name']:
            return _module
    raise NameError(f'module not find: {module}!')


def add_sub_module(module, sub_module):
    _module = get_module(module)
    _module['sub_modules'].append(
        dict(
            name=sub_module,
            functions=[]
        )
    )


def get_sub_module(module, sub_module):
    _module = get_module(module)
    for _sub_module in _module['sub_modules']:
        if sub_module == _sub_module['name']:
            return _sub_module
    raise NameError(f'sub_module not find: {module}!')


def add_function(module, sub_module, *functions):

    def fn(__sub_module, _functions):
        if len(_functions) == 1:
            __sub_module['functions'].append(
                dict(
                    name=_functions[0],
                    functions=[],
                    algorithms=[]
                )
            )
        else:
            for function in __sub_module['functions']:
                if _functions[0] == function['name']:
                    return fn(function, _functions[1:])
            raise NameError(f'function not find: {_functions[0]}!')

    _sub_module = get_sub_module(module, sub_module)
    assert len(functions) > 0, '/'.join([module, sub_module])
    return fn(_sub_module, functions)


def get_function(module, sub_module, *functions):

    def fn(__sub_module, _functions):
        for function in __sub_module['functions']:
            if _functions[0] == function['name']:
                return function if len(_functions) == 1 else fn(function, _functions[1:])
        raise NameError(f'function not find: {_functions[0]}!')

    _sub_module = get_sub_module(module, sub_module)
    assert len(functions) > 0, '/'.join([module, sub_module])
    return fn(_sub_module, functions)


def add_algorithm(module, sub_module, *functions, config):
    function = get_function(module, sub_module, *functions)
    function['algorithms'].append(
        config
    )


def get_algorithm(module, sub_module, *functions, algorithm):
    function = get_function(module, sub_module, *functions)
    for _algorithm in function['algorithms']:
        if algorithm == _algorithm['name']:
            return _algorithm
    raise NameError(f'algorithm not find: {algorithm}!')


def main():
    from pprint import pp

    add_module('模拟仿真子平台')

    add_sub_module('模拟仿真子平台', '积雪')
    add_function('模拟仿真子平台', '积雪', '模拟仿真')
    add_function('模拟仿真子平台', '积雪', '模拟仿真', '全球尺度')
    add_algorithm('模拟仿真子平台', '积雪', '模拟仿真', '全球尺度', algorithm='DTMA', config={})

    add_function('模拟仿真子平台', '积雪', '模拟仿真', '区域尺度')
    add_function('模拟仿真子平台', '积雪', '模拟仿真', '点尺度')
    add_function('模拟仿真子平台', '积雪', '模拟仿真', '模拟数据库构建')

    add_function('模拟仿真子平台', '积雪', '模拟验证')
    add_function('模拟仿真子平台', '积雪', '模拟验证', '全球尺度')
    add_function('模拟仿真子平台', '积雪', '模拟验证', '区域尺度')
    add_function('模拟仿真子平台', '积雪', '模拟验证', '点尺度')
    add_function('模拟仿真子平台', '积雪', '模拟验证', '模拟数据库构建')

    add_function('模拟仿真子平台', '积雪', '敏感性分析')
    add_function('模拟仿真子平台', '积雪', '敏感性分析', '全球尺度')
    add_function('模拟仿真子平台', '积雪', '敏感性分析', '区域尺度')
    add_function('模拟仿真子平台', '积雪', '敏感性分析', '点尺度')
    add_function('模拟仿真子平台', '积雪', '敏感性分析', '模拟数据库构建')

    add_function('模拟仿真子平台', '积雪', '载荷指标论证')
    add_function('模拟仿真子平台', '积雪', '载荷指标论证', '全球尺度')
    add_function('模拟仿真子平台', '积雪', '载荷指标论证', '区域尺度')
    add_function('模拟仿真子平台', '积雪', '载荷指标论证', '点尺度')
    add_function('模拟仿真子平台', '积雪', '载荷指标论证', '模拟数据库构建')


    add_sub_module('模拟仿真子平台', '土壤')

    add_module('数据处理子平台')

    pp(modules)
    pp(get_algorithm('模拟仿真子平台', '积雪', '模拟仿真', '全球尺度', algorithm='DTMA'))


def walk(root):

    def _add_algorithm(_root, lasts):
        path = os.path.join(_root, 'config.xlsx')
        ds = pd.read_excel(path, sheet_name=0, header=None)

        algo_name, algo_desc, executable, num_outputs = ds.iloc[:, 1].values
        algo_name = os.path.basename(_root).split('_', 1)[1]
        print('add algorithm:', '/'.join([*lasts, algo_name]))
        # print(ds.to_string(header=False, index=False))

        ds = pd.read_excel(path, sheet_name=1)
        # print(ds.to_string(header=False, index=False))
        output_params = ds.values[:num_outputs]
        config = dict(name=algo_name, description=algo_desc, work_dir=_root, executable=executable, outputs=output_params)
        add_algorithm(*lasts, config=config)

    def _add_function(*names):
        print('add function :', '/'.join(names))
        add_function(*names)

    def _walk(_root, lasts):
        for __root, dirs, files in os.walk(_root):
            # print(__root, dirs, files)
            if len(files) > 0:
                # print(__root, files)
                _add_algorithm(__root, lasts)
            elif len(dirs) > 0:
                for name in dirs:
                    function = name.split('_', 1)[1]
                    # if ...:
                    for data in os.walk(os.path.join(_root, name)):
                        if len(data[2]) == 0:
                            _add_function(*lasts, function)
                            _walk(os.path.join(_root, name), (*lasts, function))
                        else:
                            _walk(os.path.join(_root, name), lasts)
                        break
                    # _walk(os.path.join(_root, name), (*lasts, function))

            else:
                _add_function(*lasts)
            break


    root = os.path.abspath(root)
    # print(root)
    for name_0 in sorted(os.listdir(root)):
        module = name_0.split('_', 1)[1]
        add_module(module)
        for name_1 in os.listdir(os.path.join(root, name_0)):
            sub_module = name_1.split('_', 1)[1]
            add_sub_module(module, sub_module)
            _walk(os.path.join(root, name_0, name_1), (module, sub_module))
# walk('./module')
# pp(modules)
if __name__ == '__main__':
    pass
    # main()
    # ds = pd.read_excel(r"C:\Users\capino\Desktop\config.xlsx", sheet_name=0, header=None)
    # print(ds.iloc[:, 1].values)
    # for v in ds.iloc[:, 1].values:
    #     print(v, type(v))
    # print(ds)
    #
    # ds = pd.read_excel(r"C:\Users\capino\Desktop\config.xlsx", sheet_name=1)
    # print(ds)
    # print(ds.values)

    # pip install pandas openpyxl

    walk('../module')
    pp(modules)
