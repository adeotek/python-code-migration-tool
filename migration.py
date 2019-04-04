import os
import sys
import json
# import yaml
import atexit
from app_logger import AppLogger
from processor import CodeProcessor


debug_mode = 0
app_path = None
app_log = None
app_cfg = None
target_dir = None


def atexit_handler():
    app_log.logger.info('Exiting...')


atexit.register(atexit_handler)


def cfg_load(config_file):
    try:
        # JSON config
        with open(config_file + '.json', 'r') as cfg_file:
            return json.load(cfg_file)
        # # YAML config
        # with open(config_file + '.yaml', 'r') as cfg_file:
        #     return yaml.full_load(cfg_file)
    except Exception as e:
        app_log.logger.exception('Failed to load config file: %s', e)
        sys.exit()


if __name__ == '__main__':
    app_path = os.path.dirname(os.path.realpath(__file__))
    app_log = AppLogger(name='CodeMigration', debug_mode=debug_mode,
                        logs_path=os.path.join(app_path, '.logs'))
    app_cfg = cfg_load(os.path.join(app_path, 'config'))
    debug_mode = app_cfg.get('debug_mode', 0)
    if debug_mode > 0:
        app_log.setDebugMode(debug_mode)
    app_log.logger.info('Starting...')
    try:
        code_processor = CodeProcessor(app_logger=app_log, target_path=app_cfg.get('target_path', None), target_dirs=app_cfg.get(
            'target_dirs', None), file_types=app_cfg.get('file_types', None), exceptions=app_cfg.get('exceptions', None))
        code_processor.processFiles(app_cfg.get('rules', None))
    except Exception as e:
        app_log.logger.exception('Failed to start the code processor: %s', e)
        print('Failed to start the code processor: ' + str(e))
