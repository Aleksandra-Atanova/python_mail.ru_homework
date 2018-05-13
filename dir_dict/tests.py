import unittest
import os
from dir_dict import DirDict


class TestDirDict(unittest.TestCase):

    def setUp(self):
        self.directory = 'd:\python\dirdict'
        self.file_names_list = [
            'first',
            'second',
            'third'
        ]
        self.dir_dict = DirDict(self.directory)

    def test_get_full_path_to_file(self):
        for name in self.file_names_list:
            print(self.directory.join(name))
            self.assertEqual(
                self.dir_dict._get_full_path_to_file(name),
                self.directory + '\\' + name
            )

    # def test_get_list_of_files(self):
    #     self.assertEqual(
    #         self.dir_dict._get_list_of_files(),
    #         self.file_names_list
    #     )

    def test_setitem_getitem(self):
        for name in self.file_names_list:
            self.dir_dict[name] = 'value' + name
            with open(self.dir_dict._get_full_path_to_file(name), 'r', encoding='utf8') as f:
                value = f.read()
                self.assertEqual(value, self.dir_dict[name])

    def test_getitem_keyerror(self):
        with self.assertRaises(KeyError):
            a = self.dir_dict['not_in_list']

    def test_del_faulty_item(self):
        with self.assertRaises(KeyError):
            del(self.dir_dict['not_in_list'])

    def test_del_ok_item(self):
        del(self.dir_dict['first'])
        self.assertEqual(os.listdir(self.directory), ['second', 'third'])

    def test_iter(self):
        keys_list_with_iter = []
        for key in self.dir_dict:
            keys_list_with_iter.append(key)
        self.assertEqual(keys_list_with_iter, ['second', 'third'])

    def test_len(self):
        self.assertEqual(len(self.dir_dict), 2)
