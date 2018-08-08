import json
import os
from .database import Database


# TODO: enable logging


class Serializable:
    def __iter__(self):
        pass

    def __getitem__(self):
        pass


class JsonDatabase(Database):
    def load(self) -> list:
        check_program_data_files(self.filename)
        with open(self.filename, 'r') as file:
            s = file.read()
        return from_json(self.cls_seq, s)

    def unload(self, instance):
        with open(self.filename, 'w') as file:
            file.write(to_json(instance))


def check_program_data_files(file_name):
    folder_name = os.path.split(file_name)[0]
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    if not os.path.exists(file_name):
        create_storage_file(file_name)


def create_storage_file(file_name):
    with open(file_name, 'w') as file:
        file.write('[]')


def to_json(instance=None) -> str:
    def array_to_json(array):
        result = '['
        for item in array:
            if item == array[-1]:
                result = ''.join([result, to_json(item), ']'])
            else:
                result = ''.join([result, to_json(item), ', '])
        return result

    try:
        res = json.dumps(instance)
    except TypeError:
        pass
    else:
        return res

    if not isinstance(instance, list):
        attrs = vars(instance)
        res = '{'

        while attrs:
            key, value = attrs.popitem()
            if isinstance(value, list):
                res = ''.join(
                    [res, '"', key, '"', ': ', array_to_json(value)]
                )
            elif isinstance(value, Serializable):
                res = ''.join(
                    [res, '"', key, '"', ': ', to_json(value)]
                )
            elif isinstance(value, int):
                res = ''.join(
                    [res, '"', key, '"', ': ', str(value).lower()]
                )
            else:
                res = ''.join(
                    [res, '"', key, '"', ': ', '"', str(value), '"']
                )
            if attrs:
                res = ''.join([res, ', '])
        return ''.join([res, '}'])

    return array_to_json(instance)


def from_json(cls_seq: list, string):
    def make_object(num, data):
        instance = object.__new__(cls_seq[num])
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
        return instance

    def make_objects_array(num, array):
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
