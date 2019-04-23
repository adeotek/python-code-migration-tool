import re


class BaseProcessorAdapter:
    _logger = None
    _tasks = []

    def __init__(self, rules=None, app_logger=None):
        if not isinstance(rules, list) or len(rules) == 0:
            raise Exception('Invalid rules list')
        for rule in rules:
            task = self.processRule(rule)
            if isinstance(task, dict) and len(task) > 0:
                self._tasks.append(task)
        self._logger = app_logger

    def processRule(self, rule):
        task = {}
        if not isinstance(rule, dict) or len(rule) == 0:
            return task
        if not isinstance(rule['method'], str) or len(rule['method']) == 0:
            return task
        if not isinstance(rule['regex'], str) or len(rule['regex']) == 0:
            return task
        task['regex'] = re.compile(rule['regex'])
        task['method'] = getattr(self, rule['method'])
        task['method_name'] = rule['method']
        task['params'] = rule['params']
        return task

    def processData(self, data=None, results_count={}, dry_run=False, file_name=None):
        if not isinstance(data, str) or len(data) == 0:
            return data
        new_data = data
        try:
            for task in self._tasks:
                new_data = self.applyTask(task, new_data, results_count, dry_run, file_name)
        except Exception as e:
            self._logger.logger.exception('Data processing error: %s', e)
            new_data = data
        return new_data

    def applyTask(self, task, data, results_count, dry_run, file_name):
        regex = task['regex']
        method = task['method']
        for item in regex.findall(data):
            old_item = ''.join(item)
            new_item = method(item, task['params'])
            results_count['items'] += 1
            self._logger.logger.info("\n\tFile: {}\n\tMethod: [{}] \n\t\toriginal: {} \n\t\tprocessed: {}".format(
                file_name, task['method_name'], old_item, new_item))
            if not dry_run:
                data = data.replace(old_item, new_item)
        return data
