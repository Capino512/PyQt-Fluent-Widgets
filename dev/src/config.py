

title = '冰冻圈关键要素模型模拟与反演平台'


algos = [
    dict(
        id='id',
        name='name',
        description='description',
        executable='executable',
        outputs=[('name', 'postfix', 'flag')],
    )
]


# 1111 /模拟仿真子平台/积雪/模拟仿真/全球尺度
# 112
# 113

sub_funcs = [
    dict(
        name='全球尺度',
        algos=algos,
    )
]


funcs = [
    dict(
        name='模拟仿真',
        funcs=sub_funcs,
    )
]

sub_modules = [
    dict(
        name='积雪',
        funcs=funcs
    )
]


modules = [
    dict(
        name='模拟仿真子平台',
        sub_modules=sub_modules
    )
]

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
            funcs=[]
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
    assert len(functions) > 0
    return fn(_sub_module, functions)


def get_function(module, sub_module, *functions):

    def fn(__sub_module, _functions):
        for function in __sub_module['functions']:
            if _functions[0] == function['name']:
                return function if len(_functions) == 1 else fn(function, _functions[1:])
        raise NameError(f'function not find: {_functions[0]}!')

    _sub_module = get_sub_module(module, sub_module)
    assert len(functions) > 0
    return fn(_sub_module, functions)


def add_algorithm(module, sub_module, *functions, algorithm, config):
    function = get_function(module, sub_module, *functions)
    function['algorithms'].append(
        dict(
            name=algorithm,
            config=config
        )
    )


def get_algorithm(module, sub_module, *functions, algorithm):
    function = get_function(module, sub_module, *functions)
    for _algorithm in function['algorithms']:
        if algorithm == _algorithm['name']:
            return _algorithm
    raise NameError(f'algorithm not find: {algorithm}!')
