import unittest
from calistra_lib.storage.json_serializer import to_json, from_json


class JsonTests(unittest.TestCase):

    def test_int_to_json(self):
        number = 2018
        expected = "2018"
        actual = to_json(number)
        self.assertEqual(expected, actual)

    def test_empthy_string_to_json(self):
        string = ''
        expected = '""'
        actual = to_json(string)
        self.assertEqual(expected, actual)

    def test_str_1_to_json(self):
        string = "Hello World"
        expected = '"Hello World"'
        actual = to_json(string)
        self.assertEqual(expected, actual)

    def test_str_2_to_json(self):
        string = "\"foo\bar"
        expected = r'"\"foo\bar"'
        actual = to_json(string)
        self.assertEqual(expected, actual)

    def test_str_3_to_json(self):
        string = '\u1234'
        expected = r'"\u1234"'
        actual = to_json(string)
        self.assertEqual(expected, actual)

    def test_array_1_to_json(self):
        array = ['foo', {'bar': ('baz', None, 1.0, 2)}]
        expected = '["foo", {"bar": ["baz", null, 1.0, 2]}]'
        actual = to_json(array)
        self.assertEqual(expected, actual)

    def test_random_object_1_to_json(self):
        class RandomTestInstance:
            def __init__(self, first, second, third, four):
                self.first = first
                self.second = second
                self.third = third
                self.four = four

        obj = RandomTestInstance(5, 7, "Hello", "friend")
        actual = to_json(obj)
        expected_1 = '"first": 5'
        expected_2 = '"second": 7'
        expected_3 = '"third": "Hello"'
        expected_4 = '"four": "friend"'

        is_right = False
        if (actual.count(',') == 3 and
                actual.endswith('}') and
                actual.startswith('{') and
                actual.__contains__(expected_1) and
                actual.__contains__(expected_2) and
                actual.__contains__(expected_3) and
                actual.__contains__(expected_4)
        ):
            is_right = True

        self.assertEqual(True, is_right)

    def test_dict_in_list_from_json(self):
        json_str = '[{"name": "igor"}]'
        actual = from_json([dict], json_str)
        expected = [{'name': 'igor'}]
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
