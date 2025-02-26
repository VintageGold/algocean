import inspect
from typing import Union


def get_parents(obj):
    cls = resolve_class(obj)
    return list(cls.__mro__[1:-1])

def get_parent_functions(cls):
    parent_classes = get_parents(cls)
    function_list = []
    for parent in parent_classes:
        function_list += get_functions(parent)

    return list(set(function_list))

def get_functions(obj, include_parents=False):
    fn_list = []
    parent_fn_list = [] 
    # if not include_parents:
    #     parent_fn_list = get_parent_functions(cls)
    #     st.write(parent_fn_list)
    cls = resolve_class(obj)
    parent_fn_list = get_parent_functions(cls)
    for fn_name in dir(cls):
        if isinstance(getattr(cls, fn_name), property):
            continue

        if  (fn_name in parent_fn_list) and (include_parents==False):
            continue
        else:
            
            if hasattr(cls, fn_name) and callable(getattr(cls, fn_name)):
                fn_list.append(fn_name)

    return fn_list


def get_function_defaults(fn, include_null = False, mode=['input','output'],output_example_key='output_example'):
    if  not callable(fn):
        return None
    param_dict = dict(inspect.signature(fn)._parameters)
    function_defaults = {}
    assert isinstance(mode, list)

    if ( 'output' in mode): 
        function_defaults['output'] = {}

        output_example = param_dict.pop(output_example_key, {})

        if isinstance(output_example,inspect.Parameter):
            output_example = output_example._default

            if isinstance(output_example, dict):
                for k,v in output_example.items():
                    function_defaults['output'][k] = v
            elif type(output_example) in  [set,list, tuple]:
                function_defaults['output'] =  list(output_example)
            
    if ( 'input' in mode): 
        function_defaults['input'] = {}
        for k,v in param_dict.items():
            if v._default != inspect._empty and  v._default != None:
                function_defaults['input'][k] = v._default
            else:
                function_defaults['input'][k] = None

    assert isinstance(function_defaults, dict)
    assert 'output' in function_defaults
    assert 'input' in function_defaults

    return function_defaults



def get_function_schema(fn=None, include_self=True, defaults_dict=None, **kwargs):

    if defaults_dict == None:
        assert fn != None
        defaults_dict = get_function_defaults(fn=fn, **kwargs)
        if defaults_dict == None:
            defaults_dict = {}
    function_schema = {}   


    for mode_key, defaults in defaults_dict.items(): 
        function_schema[mode_key] = {}  
        if isinstance(defaults, dict):
            index_keys = list(defaults.keys())
        elif type(defaults) in  [set,list, tuple]:
            index_keys = list(range(len(defaults)))

        for k in index_keys:
            v = defaults[k]
            function_schema[mode_key][k] = type(v).__name__ \
                                                if v != None else None

    if not include_self:
        function_schema['input'].pop('self')
    return function_schema
    
    

def is_class(cls):
    '''
    is the object a class
    '''
    return type(cls).__name__ == 'type'


def is_fn_schema_complete(fn_schema):

    return  not (len(fn_schema['output'])==0 or len(fn_schema['input'])==0)
    
def get_module_function_schema(module, completed_only=False):
    cls = resolve_class(module)
    cls_function_names = get_functions(cls)
    print(get_parent_functions(cls), get_parents(cls), 'cls_function_names', module)
    schema_dict = {}
    for cls_function_name in cls_function_names:
        fn = getattr(cls, cls_function_name)
        if not callable(fn) or isinstance(fn, type):
            continue
        try:
            fn_schema = get_function_schema(fn)
        except ValueError:
            fn_schema = {'output': {}, 'input': {}}
        if not is_fn_schema_complete(fn_schema) and completed_only:
            continue
        schema_dict[cls_function_name] = fn_schema

    return schema_dict


def get_module_function_defaults(module, completed_only=False):
    cls = resolve_class(module)
    cls_function_names = get_functions(cls)
    schema_dict = {}
    for cls_function_name in cls_function_names:
        fn = getattr(cls, cls_function_name)
        fn_schema = get_function_defaults(fn)
        if not is_fn_schema_complete(fn_schema) and completed_only:
            continue
        schema_dict[cls_function_name] = get_function_defaults(fn)

    return schema_dict



def resolve_class(obj):
    '''
    resolve class of object or return class if it is a class
    '''
    if is_class(obj):
        return obj
    else:
        return obj.__class__

get_class = resolve_class



def is_full_function(fn_schema):

    for mode in ['input', 'output']:
        if len(fn_schema[mode]) > 0:
            for value_key, value_type in fn_schema[mode].items():
                if value_type == None:
                    return None
        else:
            return None
    return fn_schema 

def get_full_functions(module=None, module_fn_schemas:dict=None):
    if module_fn_schemas == None:
        assert module != None
        module_fn_schemas = get_module_function_schema(module) 
    filtered_module_fn_schemas = {}
    print(module_fn_schemas, 'WHADUP')
    for fn_key, fn_schema in module_fn_schemas.items():
        

        fn_schema['input'].pop('self')

        if is_full_function(fn_schema):
            filtered_module_fn_schemas[fn_key] = fn_schema

    return filtered_module_fn_schemas


def try_n_times(fn, max_trials:int=10, args:list=[],kwargs:dict={}):
    assert isinstance(fn, callable)
    for t in range(max_trials):
        try:
            result = fn(*args, **kwargs)
            return result
        except Exception as e:
            continue
    raise(e)
