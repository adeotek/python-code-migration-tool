from base_processor_adapter import BaseProcessorAdapter

class ProcessorAdapter(BaseProcessorAdapter):
    def prepareArgument(self, arg):
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
                pp_params += (', ' if len(pp_params) > 0 else '') + p_array[0] + ': ' + self.prepareArgument(p_array[1])
            else:
                ap_params += (', ' if len(ap_params) > 0 else '') + self.prepareArgument(p)
        return { 'params': pp_params, 'aparams': ap_params }

    def ajaxParamsStringConvert(self, command):
        # print('command: {}'.format(command))
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
            params += "'module': " + p_list[0] + ","
            params += "'method': " + p_list[1] + ","
            p_params = p_list[2] if len(p_list) > 2 else ''            
            t_params = self.processExtraParamsString(p_params)
            pp_params = t_params['params']
            pp_params += (', ' if len(pp_params) else '') + "'target': "
            if len(p_list) > 3:
                pp_params += p_list[3]
            else:
                pp_params += "''"
            params += "'params': { " + pp_params + ' }'
            if len(t_params['aparams']):
                params += ", 'arrayParams': [ " + t_params['aparams'] + ' ]'
        params = '{ ' + (params if isinstance(params, str) else '') + ' }'
        return { 'params': params, 'target_id': target_id, 'jparams': jparams, 'eparams': eparams }

    def command_string(self, data):
        params = self.ajaxParamsStringConvert(data[19:-2])
        return "'ajax_command'=>\"{}\",\n'ajax_target_id'=>'{}',".format(params['params'], params['target_id'])

    def onclick_legacy_prepare(self, data):
        params = self.ajaxParamsStringConvert(data[52:-3])
        return "'onclick'=>NApp::Ajax()->Prepare(\"{}\",'{}'),".format(params['params'], params['target_id'])
