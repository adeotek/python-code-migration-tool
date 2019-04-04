import os
import glob
import re


class CodeProcessor:
    _logger = None
    _target_path = None
    _target_dirs = None
    _file_types = None
    _exception_files = None
    _exception_directories = None
    _files = None

    def __init__(self, target_path=None, target_dirs=None, file_types=None, exceptions=None, app_logger=None):
        if target_path is None or not os.path.exists(target_path):
            raise Exception(
                'Invalid target path: [' + target_path or 'none' + ']')
        if target_dirs is None or not isinstance(target_dirs, list):
            raise Exception('Invalid target directories list')
        self._target_path = target_path
        self._target_dirs = target_dirs
        self._file_types = file_types
        if isinstance(exceptions, dict):
            self._exception_files = exceptions['files']
            self._exception_directories = exceptions['directories']
        self._logger = app_logger

    def processFiles(self, rules=None):
        # if not isinstance(reg_exp, str) or len(reg_exp) == 0:
        #     raise Exception('Invalid regular expresion string')
        # re_exp = re.compile(reg_exp, re.MULTILINE)
        print('Target path: ' + self._target_path)
        for dir_name in self._target_dirs:
            if os.path.exists(os.path.join(self._target_path, dir_name)):
                for entry in self.getFilesFromPath(target_dir=os.path.join(self._target_path, dir_name), file_types=self._file_types, exception_files=self._exception_files, exception_directories=self._exception_directories):
                    print('File: [{}] [{}]'.format(entry.path, entry.name))
                    data = self.getMatchingStringsFromFile(entry.path, None)
                    print(*data, sep="\n")

    def getFilesFromPath(self, target_dir=None, file_types=None, exception_files=None, exception_directories=None):
        for entry in os.scandir(target_dir):
            if entry.is_file():
                file_ext = os.path.splitext(entry.name)[1].lower()
                if file_ext not in file_types or (isinstance(exception_files, list) and entry.name in exception_files):
                    continue
                yield entry
            elif entry.is_dir():
                if isinstance(exception_directories, list) and entry.name in exception_directories:
                    continue
                yield from self.getFilesFromPath(target_dir=entry.path, file_types=file_types, exception_files=exception_files, exception_directories=exception_directories)

    def getMatchingStringsFromFile(self, file, reg_exp):
        # if not isinstance(reg_exp, object):
        #     raise Exception('Invalid regular expresion object')
        if not os.path.exists(file):
            return []
        with open(file, 'r') as cfile:
            file_content = cfile.read()
            # return reg_exp.findall(file_content)
            return re.findall(r"'command_string'=>\"AjaxRequest\(.*\)->.*\",", file_content, re.MULTILINE)
