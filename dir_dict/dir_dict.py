from collections import MutableMapping
import os


class DirDict(MutableMapping):

    def __init__(self, directory):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def _get_full_path_to_file(self, key):
        full_path_to_file = os.path.join(self.directory, key)
        return full_path_to_file

    def _get_list_of_files(self):
        list_of_files = os.listdir(self.directory)
        return list_of_files

    def __setitem__(self, key, value):
        with open(self._get_full_path_to_file(key), 'w', encoding='utf8') as f:
            f.write(value if isinstance(value, str) else repr(value))

    def __getitem__(self, key):
        if key not in self._get_list_of_files():
            raise KeyError(key)
        with open(self._get_full_path_to_file(key), 'r', encoding='utf8') as f:
            return f.read()

    def __delitem__(self, key):
        if key not in self._get_list_of_files():
            raise KeyError(key)
        os.remove(self._get_full_path_to_file(key))

    def __iter__(self):
        return iter(self._get_list_of_files())

    def __len__(self):
        return len(self._get_list_of_files())
