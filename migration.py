import os
import sys
from app_logger import AppLogger
import config_loader as cfg_loader
from processor import CodeProcessor


debug_mode = 0
dry_run = False
app_path = None
app_log = None
app_cfg = None
target_dir = None


if __name__ == '__main__':
    app_path = os.path.dirname(os.path.realpath(__file__))
    app_log = AppLogger(name='CodeMigration', debug_mode=debug_mode,
                        logs_path=os.path.join(app_path, '.logs'))
    try:
        app_cfg = cfg_loader.load(os.path.join(app_path, 'config'), 'json')
    except Exception as e:
        app_log.logger.exception('Failed to load config file: %s', e)
        sys.exit()
    debug_mode = 1 if '--debug' in sys.argv else app_cfg.get('debug_mode', debug_mode)
    if debug_mode > 0:
        app_log.setDebugMode(debug_mode)
    dry_run = bool(1 if '--dry-run' in sys.argv else app_cfg.get('dry_run', dry_run))
    app_log.logger.info('Starting{}...'.format(' DRY-RUN' if dry_run else ''))
    try:
        code_processor = CodeProcessor(app_logger=app_log, target_path=app_cfg.get('target_path', None), target_dirs=app_cfg.get(
            'target_dirs', None), file_types=app_cfg.get('file_types', None), exceptions=app_cfg.get('exceptions', None))
        code_processor.processFiles(tasks=app_cfg.get('tasks', None), dry_run=dry_run)
    except Exception as e:
        app_log.logger.exception('Failed to start the code processor: %s', e)
