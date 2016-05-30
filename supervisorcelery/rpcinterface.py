import ConfigParser

import supervisor.loggers

from supervisor.options import UnhosedConfigParser, ProcessConfig
from supervisor.datatypes import list_of_strings
from supervisor.states import SupervisorStates
from supervisor.states import STOPPED_STATES
from supervisor.xmlrpc import Faults as SupervisorFaults
from supervisor.xmlrpc import RPCError


API_VERSION = '1.0'


class ConfigReaderNamespaceRPCInterface(object):
    """
    """
    def __init__(self, supervisord, **config):
        self.supervisord = supervisord

    def _update(self, func_name):
        self.update_text = func_name

    # RPC API method
    def get_api_version(self):
        self._update('get_api_version')
        return API_VERSION

    def get_test(self):
        self._update('get_test')

        configfile = self.supervisord.options.configfile
        config = ConfigParser.RawConfigParser()
        config.read(configfile)
        proc_section = 'program:red'
        workernames = config.get(proc_section, 'workernames')
        tasks = config.get(proc_section, 'tasks')
        concurrency = config.getint(proc_section, 'concurrency')
        loglevel = config.get(proc_section, 'loglevel')
        logfile = config.get(proc_section, 'logfile')
        pidfile = config.get(proc_section, 'pidfile')
        group = self._get_process_group('red')
        print(group)
        options = self.supervisord.options
        proc_command = ('celery multi start {workers} -A {tasks} '
                        '--concurrency={concurrency} '
                        '--loglevel={loglevel} '
                        '--logfile={logfile} '
                        '--pidfile={pidfile}'.format(
            workers=workernames,
            tasks=tasks,
            concurrency=concurrency,
            loglevel=loglevel,
            logfile=logfile,
            pidfile=pidfile
        ))
        print(proc_command)
        proc_config = {
            'command': 'cat',
            'autostart': True
        }
        parser = self._make_config_parser(proc_section, proc_config)
        try:
            new_configs = options.processes_from_section(parser, proc_section, group)
        except ValueError as e:
            raise RPCError(SupervisorFaults.INCORRECT_PARAMETERS, e)

        assert len(new_configs) == 1, 'We can create only one config at a time'
        new_config = new_configs[0]
        # Override configuration for the program to use with celery multi
        import pdb; pdb.set_trace()
        new_config.create_autochildlogs()
        group.processes[new_config.name] = new_config.make_process(group)

        return True

    def log(self, message, level=supervisor.loggers.LevelsByName.INFO):
        self._update('log')

        if isinstance(level, str):
            level = getattr(supervisor.loggers.LevelsByName,
                            level.upper(), None)

        if supervisor.loggers.LOG_LEVELS_BY_NUM.get(level, None) is None:
            raise RPCError(SupervisorFaults.INCORRECT_PARAMETERS)

        self.supervisord.options.logger.log(level, message)
        return True

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
