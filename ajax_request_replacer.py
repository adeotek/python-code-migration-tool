import re
from base_processor_adapter import BaseProcessorAdapter

class ProcessorAdapter(BaseProcessorAdapter):
    _target_regex = None

    def __init__(self, rules=None, app_logger=None):
        self._target_regex = re.compile(r'^\{\$\w+\}$')
        super().__init__(rules=rules, app_logger=app_logger)

    def prepareArgument(self, arg):
        arg = arg.strip('" \t\n\r')
        if ':' in arg:
            return "'{nGet|" + arg + "}'"
        if arg.strip("'") == arg and '(' in arg and ')' in arg:
            return "'{nEval|" + arg + "}'"
        return arg

    def processExtraParamsString(self, params):
        pp_params = ''
        ap_params = ''
        if not isinstance(params, str) or len(params) == 0:
            return { 'params': pp_params, 'aparams': ap_params }        
        for p in params.split('~'):
            if '|' in p:
                p_array = p.split('|')
                pp_params += (', ' if len(pp_params) > 0 else '') + p_array[0].strip('" \t\n\r') + ': ' + self.prepareArgument(p_array[1])
            else:
                ap_params += (', ' if len(ap_params) > 0 else '') + self.prepareArgument(p)
        return { 'params': pp_params, 'aparams': ap_params }

    def ajaxParamsStringConvert(self, command):
        params = ''
        target_id = ''
        jparams = {}
        eparams = None
        first = True
        for it in command.split('-<'):
            it = it.strip()
            if first:
                first = False
                command = it
            elif len(it) > 0:
                jparams[it] = it
        if "->{ uploadedfile: '#uploadedfile#' }" in command:
            eparams = "{ 'uploadedfile': '#uploadedfile#' }"
            command = command.replace("->{ uploadedfile: '#uploadedfile#' }", '')
        tmp = command.split(')->')
        if len(tmp) > 2:
            function = ')->'.join(tmp[0:-1])
            target_id = tmp[-1].strip()
        elif len(tmp) == 2:
            function = tmp[0].strip()
            target_id = tmp[1].strip()
        else:
            function = tmp[0].strip()
            target_id = ''
        if 'AjaxRequest(' in function:
            args = function.replace('AjaxRequest(', '')
        else:
            args = function
        if len(args) > 0:
            p_list = args.split(',')
            params += "'module': " + p_list[0].strip('" \t\n\r') + ", "
            params += "'method': " + p_list[1].strip('" \t\n\r') + ", "
            p_params = p_list[2] if len(p_list) > 2 else ''            
            t_params = self.processExtraParamsString(p_params)
            pp_params = t_params['params']
            if len(p_list) > 3:
                pp_params += (', ' if len(pp_params) else '') + "'target': " + p_list[3].strip('" \t\n\r')
            params += "'params': { " + pp_params + ' }'
            if len(t_params['aparams']):
                params += ", 'arrayParams': [ " + t_params['aparams'] + ' ]'
        params = '{ ' + (params if isinstance(params, str) else '') + ' }'
        return { 'params': params, 'target_id': target_id, 'jparams': jparams, 'eparams': eparams }

    def process_target_id_val(self, target_id):
        if not isinstance(target_id, str) or len(target_id) == 0:
            return "''"
        matched = self._target_regex.search(target_id)
        if isinstance(matched, re.Match) and matched.group() == target_id:
            return target_id.strip('}{')
        return "'{}'".format(target_id)

    def legacy_prepare_string(self, data, extra_params):
        if len(data) != 5:
            raise Exception('Invalid regex groups: {}'.format(str(data)))
        new_prefix = extra_params['new_prefix'] if isinstance(extra_params['new_prefix'], str) else ''
        sufix = extra_params['sufix'] if 'sufix' in extra_params.keys() and isinstance(extra_params['sufix'], str) else ''
        params = self.ajaxParamsStringConvert(data[3])
        new_sufix = ''
        if len(sufix) > 0:
            new_sufix = sufix if r'{}' not in extra_params['sufix'] else sufix.format(self.process_target_id_val(params['target_id']))
        new_data = '{}{}{}{}{}{}'.format(data[0], new_prefix, data[2], params['params'], data[4].strip("\r"), new_sufix)
        return new_data
    
    def legacy_prepare_method(self, data, extra_params):
        if len(data) != 5:
            raise Exception('Invalid regex groups: {}'.format(str(data)))
        params = self.ajaxParamsStringConvert(data[2])
        return '{}Prepare("{}",{}{}'.format(data[0], params['params'], self.process_target_id_val(params['target_id']), data[4].strip("\r"))

    def legacy_execute_method(self, data, extra_params):
        if len(data) != 5:
            raise Exception('Invalid regex groups: {}'.format(str(data)))
        params = self.ajaxParamsStringConvert(data[2])
        return '{}Execute("{}",{}{}'.format(data[0], params['params'], self.process_target_id_val(params['target_id']), data[4].strip("\r"))

