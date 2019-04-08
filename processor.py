import os
import datetime
from importlib import import_module

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

    def processFiles(self, tasks=None, dry_run=False):
        if not isinstance(tasks, list) or len(tasks) == 0:
            raise Exception('Invalid processing rules')
        print('--->Start processing path: {}...'.format(self._target_path))
        start_time = datetime.datetime.now()
        adapters = []
        for task in tasks:
            try:
                if not isinstance(task['module'], str) or len(task['module']) == 0:
                    raise Exception('Invalid task module')
                if not isinstance(task['rules'], list) or len(task['rules']) == 0:
                    raise Exception('Invalid task rules')
                adapter_module = import_module(task['module'])
                adapters.append(adapter_module.ProcessorAdapter(rules=task['rules'], app_logger=self._logger))
            except Exception as e:
                print("Unable to create processor adapter: [{}] -> {}". format(task, e))
                return
        for dir_name in self._target_dirs:
            if os.path.exists(os.path.join(self._target_path, dir_name)):
                for entry in self.getFilesFromPath(target_dir=os.path.join(self._target_path, dir_name), file_types=self._file_types, exception_files=self._exception_files, exception_directories=self._exception_directories):
                    self.processFile(entry.path, adapters, dry_run)
        print('<---Processing done in: {} sec.'.format((datetime.datetime.now() - start_time).total_seconds()))

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

    def processFile(self, file, adapters, dry_run):
        if not os.path.exists(file):
            return
        if not isinstance(adapters, list):
            raise Exception('No adapters present')
        file_content = None
        with open(file, 'r') as cfile:
            file_content = cfile.read()
            cfile.close()
        if isinstance(file_content, str) and len(file_content) > 0:
            print('Processing file: [{}]...'.format(file))
            for adapter in adapters:
                file_content = adapter.processData(data=file_content, dry_run=dry_run)
            with open(file, 'w') as cfile:
                cfile.write(file_content)
                cfile.close()
