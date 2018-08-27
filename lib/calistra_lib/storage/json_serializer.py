import json


def concat(*args):
    return ''.join(args)


class Serializable:
    """
    This class using as indicator for models and shows that it can serialize
    """
    def __iter__(self):
        pass

    def __getitem__(self):
        pass


class JsonDatabase:
    """
    This class describe mechanism which parse data in json format
    """
    def __init__(self, filename, cls_seq=None):
        """
        Init method. Calling after creating instance
        :param filename: file where instance stored
        :param cls_seq:  sequence of classes represent nested objects
        of instance
        """
        if cls_seq is None:
            cls_seq = []
        self.cls_seq = cls_seq
        self.filename = filename

    def load(self) -> list:
        """
        This method parse from json object in python object
        :return: instance
        """
        with open(self.filename, 'r') as file:
            s = file.read()
        return from_json(self.cls_seq, s)

    def unload(self, instance):
        """
        This method parse python object to string in json format
        :param instance: instance for parsing
        :return: None
        """
        with open(self.filename, 'w') as file:
            file.write(to_json(instance, indentation=4))


def array_to_json(array, ctrl_char, indent, level):
    """
    This method parse array into json
    :param array: array for parsing
    :param ctrl_char: control char
    :param indent:
    :param level:
    :return: string in json format
    """
    if not array:
        return '[]'
    result = ''.join(['[', ctrl_char, ' ' * level * indent])

    size = len(array)
    for i in range(size):
        item = array[i]
        if i == size - 1:
            # if array item is last in array to result string will be appended
            #  right square bracket because json-string is ready
            result = ''.join(
                [
                    result,
                    to_json(item, indent, level+1),
                    ctrl_char,
                    ' ' * (level - 1) * indent, ']'
                ]
            )
        else:
            result = ''.join(
                [
                    result,
                    to_json(item, indent, level+1),
                    ',',
                    ctrl_char,
                    ' ' * level * indent
                ]
            )
    return result


def to_json(instance=None, indentation=None, level=1) -> str:
    """
    This method parse instance into json format
    :param instance: instance for parsing
    :param indentation:
    :param level: level of indentation
    :return: string in json format
    """

    # try to parse object by default json parser
    try:
        res = json.dumps(instance, indent=indentation)
    except TypeError:
        pass
    else:
        return res

    # if indentation is define use it for parsing objects with indentation
    if indentation is None:
        indent = 0
        ctrl_char = ''
    else:
        indent = indentation
        ctrl_char = '\n'

    # parse non-list objects
    if not isinstance(instance, list):

        # get instance args as dict if it possible else attrs will be defined
        # as instance
        try:
            attrs = vars(instance).copy()
        except TypeError:
            attrs = instance

        # form begin of result string in json format
        res = ''.join(['{', ctrl_char, ' ' * level * indent])

        while attrs:
            # parse every instance attr in json format
            key, value = attrs.popitem()
            if isinstance(value, list):
                # if attr is list parse it as array
                res = ''.join(
                    [res, '"', key, '"', ': ',
                     array_to_json(value, ctrl_char, indent, level + 1)]
                )
            elif isinstance(value, Serializable):
                # if attr is Serializable object instance parse it as instance
                res = ''.join(
                    [res, '"', key, '"', ': ', to_json(value, indent, level + 1)]
                )
            elif isinstance(value, int):
                # if attr is int, it append to result string
                res = ''.join(
                    [res, '"', key, '"', ': ', str(value).lower()]
                )
            elif value is None:
                # if attr is None, append null to result
                res = ''.join(
                    [res, '"', key, '"', ': ', 'null']
                )
            else:
                res = ''.join(
                    [res, '"', key, '"', ': ', '"', str(value), '"']
                )
            if attrs:
                # if attrs not empty in string append comma
                res = ''.join([res, ',', ctrl_char, ' ' * level * indent])
        # end of parsing non list object
        return ''.join([res, ctrl_char, ' ' * (level-1) * indent, '}'])

    # parse list objects
    return array_to_json(instance, ctrl_char, indentation, level)


def from_json(cls_seq: list, string):
    """
    Parse string in json format and return instance
    :param cls_seq: sequence of classes of object inside instance
    :param string: string in json format
    :return: instance
    """
    def set_dict_attr(instance, data, num):
        """
        This nested function set value of all instance attr
        :param instance: instance to set it attrs
        :param data:
        :param num:
        :return:
        """
        for key, value in data.items():
            if isinstance(value, list):
                instance[key] = make_objects_array(num + 1, value)
            elif isinstance(value, dict):
                instance[key] = make_object(num + 1, value)
            else:
                instance[key] = value

    def set_object_attr(instance, data, num):
        """
        For object set its attrs
        :param instance:
        :param data:
        :param num: number of class in class sequence
        :return: None
        """
        for key, value in data.items():
            if isinstance(value, list):
                # for key set result of making list of objects if value is list
                setattr(instance, key, make_objects_array(num + 1, value))
            elif isinstance(value, dict):
                # for key set result of making simple object if value is dict
                setattr(instance, key, make_object(num + 1, value))
            else:
                setattr(instance, key, value)

    def make_object(num, data):
        """
        This method collect object
        :param num: number of class in class sequence
        :param data:
        :return: instance
        """
        if cls_seq[num] is dict:
            # if instance is dict, create a dict
            instance = dict.__new__(dict)
            set_dict_attr(instance, data, num)
        else:
            # if instance is object, create object
            instance = object.__new__(cls_seq[num])
            set_object_attr(instance, data, num)
        return instance

    def make_objects_array(num, array):
        """
        This method create array of objects
        :param num:
        :param array:
        :return: array of objects
        """
        entity = []
        for item in array:
            if isinstance(item, list):
                # append a list of nested instances objects
                entity.append(make_objects_array(num + 1, item))
            elif isinstance(item, dict):
                # append simple object
                entity.append(make_object(num, item))
            else:
                entity.append(item)
        return entity

    # using standart json library, from parse string in json format in
    # set of dicts and lists
    py_objs = json.loads(string)

    if isinstance(py_objs, list):
        return make_objects_array(0, py_objs)

    if isinstance(py_objs, int):
        return py_objs

    if isinstance(py_objs, str):
        return py_objs

    return make_object(0, py_objs)
