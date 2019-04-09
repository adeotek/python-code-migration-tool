from base_processor_adapter import BaseProcessorAdapter

class ProcessorAdapter(BaseProcessorAdapter):
    def prepareArgument(self, arg):
        arg = arg.strip('" \t\n')
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
                pp_params += (', ' if len(pp_params) > 0 else '') + p_array[0].strip('" \t\n') + ': ' + self.prepareArgument(p_array[1])
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
            params += "'module': " + p_list[0].strip('" \t\n') + ", "
            params += "'method': " + p_list[1].strip('" \t\n') + ", "
            p_params = p_list[2] if len(p_list) > 2 else ''            
            t_params = self.processExtraParamsString(p_params)
            pp_params = t_params['params']
            pp_params += (', ' if len(pp_params) else '') + "'target': "
            if len(p_list) > 3:
                pp_params += p_list[3].strip('" \t\n')
            else:
                pp_params += "''"
            params += "'params': { " + pp_params + ' }'
            if len(t_params['aparams']):
                params += ", 'arrayParams': [ " + t_params['aparams'] + ' ]'
        params = '{ ' + (params if isinstance(params, str) else '') + ' }'
        return { 'params': params, 'target_id': target_id, 'jparams': jparams, 'eparams': eparams }

    def command_string(self, data, extra_params):
        params = self.ajaxParamsStringConvert(data[19:-2])
        return "'ajax_command'=>\"{}\",\n'ajax_target_id'=>'{}',".format(params['params'], params['target_id'])

    def onclick_str(self, data, extra_params):
        params = self.ajaxParamsStringConvert(data[19:-2])
        return "'onclick_ajax_command'=>\"{}\",\n'onclick_target_id'=>'{}',".format(params['params'], params['target_id'])

    def tab_ajax_content(self, data, extra_params):
        params = self.ajaxParamsStringConvert(data[19:-2])
        return "'content_ajax_command'=>\"{}\",".format(params['params'])

    def legacy_execute(self, data, extra_params):
        params = self.ajaxParamsStringConvert(data[52:-3])
        return "NApp::Ajax()->Execute(\"{}\",'{}');".format(params['params'], params['target_id'])
    
    def action_legacy_prepare(self, data, extra_params):
        params = self.ajaxParamsStringConvert(data[52:-3])
        action = extra_params['action'] if isinstance(extra_params['action'], str) else ''
        end_char = extra_params['end_char'] if isinstance(extra_params['end_char'], str) else ''
        return "'{}'=>NApp::Ajax()->Prepare(\"{}\",'{}'){}".format(action, params['params'], params['target_id'], end_char)

    def echo_legacy_prepare(self, data, extra_params):
        params = self.ajaxParamsStringConvert(data[52:-3])
        return "=\"<?=NApp::Ajax()->Prepare(\"{}\",'{}')?>\"".format(params['params'], params['target_id'])


