import json
from .database import Database


# TODO: 1) дописать документацию
# TODO: 2) Рефакторинг
# TODO: 3) Логгирование
# TODO: 4) все объединить в процедуру конкат

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


class JsonDatabase(Database):
    """
    This class describe mechanism which parse data in json format
    """
    def load(self) -> list:
        with open(self.filename, 'r') as file:
            s = file.read()
        return from_json(self.cls_seq, s)

    def unload(self, instance):
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
    try:
        res = json.dumps(instance, indent=indentation)
    except TypeError:
        pass
    else:
        return res

    if indentation is None:
        indent = 0
        ctrl_char = ''
    else:
        indent = indentation
        ctrl_char = '\n'

    if not isinstance(instance, list):
        try:
            attrs = vars(instance).copy()
        except TypeError:
            attrs = instance
        res = ''.join(['{', ctrl_char, ' ' * level * indent])

        while attrs:
            key, value = attrs.popitem()
            if isinstance(value, list):
                res = ''.join(
                    [res, '"', key, '"', ': ',
                     array_to_json(value, ctrl_char, indent, level + 1)]
                )
            elif isinstance(value, Serializable):
                res = ''.join(
                    [res, '"', key, '"', ': ', to_json(value, indent, level + 1)]
                )
            elif isinstance(value, int):
                res = ''.join(
                    [res, '"', key, '"', ': ', str(value).lower()]
                )
            elif value is None:
                res = ''.join(
                    [res, '"', key, '"', ': ', 'null']
                )
            else:
                res = ''.join(
                    [res, '"', key, '"', ': ', '"', str(value), '"']
                )
            if attrs:
                res = ''.join([res, ',', ctrl_char, ' ' * level * indent])
        return ''.join([res, ctrl_char, ' ' * (level-1) * indent, '}'])

    return array_to_json(instance, ctrl_char, indentation, level)


def from_json(cls_seq: list, string):
    """
    Parse string in json format and return instance
    :param cls_seq: sequence of classes of object inside instance
    :param string: string in json format
    :return: instance
    """
    def set_dict_attr(instance, data, num):
        for key, value in data.items():
            if isinstance(value, list):
                # print('list in make_object')
                instance[key] = make_objects_array(num + 1, value)
            elif isinstance(value, dict):
                # print('obj in make_object')
                instance[key] = make_object(num + 1, value)
            else:
                # print('item in make object')
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
                # print('list in make_object')
                setattr(instance, key, make_objects_array(num + 1, value))
            elif isinstance(value, dict):
                # print('obj in make_object')
                setattr(instance, key, make_object(num + 1, value))
            else:
                # print('item in make object')
                setattr(instance, key, value)

    def make_object(num, data):
        """
        This method collect object
        :param num: number of class in class sequence
        :param data:
        :return: instance
        """
        if cls_seq[num] is dict:
            instance = dict.__new__(dict)
            set_dict_attr(instance, data, num)
        else:
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
            # print(item)
            if isinstance(item, list):
                # print('TO_LIST')
                entity.append(make_objects_array(num + 1, item))
            elif isinstance(item, dict):
                # print('TO_CLASS')
                entity.append(make_object(num, item))
            else:
                # print('SIMPLE_OBJECT')
                entity.append(item)
        return entity

    py_objs = json.loads(string)

    if isinstance(py_objs, list):
        return make_objects_array(0, py_objs)

    if isinstance(py_objs, int):
        return py_objs

    if isinstance(py_objs, str):
        return py_objs

    return make_object(0, py_objs)
