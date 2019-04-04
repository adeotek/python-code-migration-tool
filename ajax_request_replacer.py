import re

class ProcessorAdapter:
    _logger = None
    _regex = None
    _method_name = None
    _method = None
    
    def __init__(self, regex=None, method=None, app_logger=None):
        if not isinstance(regex, str) or len(regex) == 0:
            raise Exception('Invalid regular expresion string')
        self._regex = re.compile(regex, re.MULTILINE)
        self._method_name = method
        self._method = method = getattr(self, method)
        self._logger = app_logger
        
    def processData(self, data=None):
        if not isinstance(data, str) or len(data) == 0:
            return data
        # print(*data, sep="\n")
        for item in self._regex.findall(data):
            new_item = self._method(item)
            print("\tMethod: [{}] \n\t\toriginal: {} \n\t\tprocessed: {}".format(self._method_name, item, new_item))
        # return data.replace(item, new_item)
        return data

    def ajaxParamsStringConvert(self, params):
        print('params: {}'.format(params))
        command = None
        functions = None
        targets = None
        jparams = {}
        eparams = None
        first = True
        for it in params.split('-<'):
            if first:
                first = False
                command = it.trim()
            elif len(it.trim()) > 0:
                jparams[it.trim()] = it.trim()
        tmp = command.trim().split('->')
        if isinstance(tmp[0], str) and len(tmp[0].trim()) > 0:
            functions = tmp[0].trim()
        if isinstance(tmp[1], str) and len(tmp[1].trim()) > 0:
            targets = tmp[1].trim()
        if isinstance(tmp[2], str) and len(tmp[2].trim()) > 0:
            eparams = tmp[2].trim()
        # old_params, target_id = data.split(')-')
        # new_params = "{  }"
        
        return { 'params': '{ }', 'target_id': 'xxx' }

    def command_string(self, data):
        params = self.ajaxParamsStringConvert(data[19:-2])
        return "'ajax_command'=>\"{}\",\n'ajax_target_id'=>'{}',".format(params['params'], params['target_id'])
