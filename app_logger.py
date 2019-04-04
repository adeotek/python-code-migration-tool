import os
import logging
import time

class AppLogger:
    logger = None
    _handlers = {}
    _formatter = None
    _logs_path = None

    def __init__(self, name=None, debug_mode=0, logs_path=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.WARN)
        if logs_path:
            try:
                if not os.path.exists(logs_path):
                    os.makedirs(logs_path)
                self._logs_path = logs_path
                self.addFileHandler(
                    'errors.log', self._logs_path, logging.WARN)
            except Exception as e:
                print('Exception: ', e)
                self._logs_path = None
        self.setDebugMode(debug_mode)

    def setDebugMode(self, debug_mode):
        if debug_mode > 0:
            self.logger.setLevel(logging.DEBUG)
            if (debug_mode == 1 or debug_mode == 11) and self._logs_path:
                self.addFileHandler('debugging.log', self._logs_path, logging.DEBUG)
            if debug_mode == 10 or debug_mode == 11:
                self.addConsoleHandler('console', logging.DEBUG)
        else:
            self.logger.setLevel(logging.WARN)
            if 'debugging.log' in self._handlers:
                self.logger.removeHandler(self._handlers['debugging.log'])
                del(self._handlers['debugging.log'])
            if 'console' in self._handlers:
                self.logger.removeHandler(self._handlers['console'])
                del(self._handlers['console'])
    
    def addConsoleHandler(self, name, level):
        # create new console handler
        if name not in self._handlers:
            self._handlers[name] = logging.StreamHandler()
            self._handlers[name].setLevel(level)
            self._handlers[name].setFormatter(self.getFormatter())
            self.logger.addHandler(self._handlers[name])

    def addFileHandler(self, name, logs_path, level):
        # create new file handler
        if name not in self._handlers:
            self._handlers[name] = logging.FileHandler(os.path.join(logs_path, name))
            self._handlers[name].setLevel(level)
            self._handlers[name].setFormatter(self.getFormatter())
            self.logger.addHandler(self._handlers[name])

    def setFormatter(self, formatter):
        self._formatter = formatter

    def getFormatter(self):
        if self._formatter is None:
            return self.getDefaultFormatter()
        return self._formatter

    def getDefaultFormatter(self):
        # create default formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        return formatter
