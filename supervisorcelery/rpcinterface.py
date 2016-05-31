import ConfigParser

import supervisor.loggers

from supervisor.options import UnhosedConfigParser, ProcessConfig
from supervisor.states import SupervisorStates
from supervisor.states import ProcessStates
from supervisor.xmlrpc import Faults as SupervisorFaults
from supervisor.xmlrpc import RPCError


API_VERSION = '1.0'


class ConfigReaderNamespaceRPCInterface(object):
    """
    """
    CELERY_MULTI_COMMAND_TMPL = 'celery multi {command} {args}'

    def __init__(self, supervisord, **config):
        self.supervisord = supervisord

    def _update(self, func_name):
        self.update_text = func_name

    # RPC API method
    def get_api_version(self):
        self._update('get_api_version')
        return API_VERSION

    def _create_command(self, command, args):
        return self.CELERY_MULTI_COMMAND_TMPL.format(command=command, 
                                                     args=args)

    def _extract_params(self, proc_name, proc_section):
        configfile = self.supervisord.options.configfile
        config = ConfigParser.RawConfigParser()
        config.read(configfile)

        req_params = ('workernames', 'tasks')
        opt_params = ('concurrency', 'loglevel', 'logfile', 'pidfile')
        params_dict = {}
        for param in req_params:
            try:
                params_dict[param] = config.get(proc_section, param)
            except ConfigParser.NoOptionError:
                raise RPCError(SupervisorFaults.BAD_ARGUMENTS)

        req_command = '{workernames} -A {tasks} '.format(**params_dict)
        opt_command = ''
        for param in opt_params:
            param_value = None
            try:
                param_value = config.get(proc_section, param)
            except ConfigParser.NoOptionError:
                pass

            if param_value is not None:
                opt_command += '--{param}={param_value} '.format(
                        param=param,
                        param_value=param_value)

        # Replace supervisor special chars to use celery wildcards
        command = req_command + opt_command.replace('%%', '%')
        return command

    def start_app(self, proc_name):
        self._update('start_app')

        proc_section = 'program:{proc_name}'.format(proc_name=proc_name)
        group = self._get_process_group(proc_name)
        fake_process = group.processes[proc_name]

        celery_command = 'start'
        command_args = self._extract_params(proc_name, proc_section)

        proc_config = {
            'command': self._create_command(celery_command, command_args),
            'autostart': True,
            'startretries': 0,
            'startsecs': 0,
        }

        # Override configuration for the program to use with celery multi
        merged_config = self._merge_configs(fake_process.config, proc_config)

        group.processes[proc_name] = merged_config.make_process(group)
        current_proc = group.processes[proc_name]
        current_proc.spawn()
        # todo (misha): change process state
        current_proc.change_state(ProcessStates.RUNNING)
        return True

    def restart_app(self, proc_name):
        self._update('restart_app')
        celery_command = 'restart'

    def stop_app(self, proc_name):
        self._update('stop_app')
        celery_command = 'stop'

    def log(self, message, level=supervisor.loggers.LevelsByName.INFO):
        self._update('log')

        if isinstance(level, str):
            level = getattr(supervisor.loggers.LevelsByName,
                            level.upper(), None)

        if supervisor.loggers.LOG_LEVELS_BY_NUM.get(level, None) is None:
            raise RPCError(SupervisorFaults.INCORRECT_PARAMETERS)

        self.supervisord.options.logger.log(level, message)
        return True

    def _merge_configs(self, old_config, new_config):
        for key, value in old_config.__dict__.items():
            if key in new_config:
                setattr(old_config, key, new_config[key])
        return old_config

    def _get_process_group(self, name):
        """ Find a process group by its name """
        group = self.supervisord.process_groups.get(name)
        if group is None:
            raise RPCError(SupervisorFaults.BAD_NAME, 'group: %s' % name)
        return group

    def _make_config_parser(self, section_name, options):
        config_parser = UnhosedConfigParser()
        try:
            config_parser.add_section(section_name)
            for key, value in dict(options).items():
                config_parser.set(section_name, key, value)
        except (TypeError, ValueError) as e:
            return RPCError(SupervisorFaults.INCORRECT_PARAMETERS)

        return config_parser


def make_config_reader_rpcinterface(supervisord, **config):
    return ConfigReaderNamespaceRPCInterface(supervisord, **config)
