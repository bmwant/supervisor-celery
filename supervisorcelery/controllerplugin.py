from supervisor.supervisorctl import ControllerPluginBase


class CeleryMultiControllerPlugin(ControllerPluginBase):
    name = 'celerymulti'

    def __init__(self, controller, **config):
        self.ctl = controller
        print(config)

    def _expand_wildcards(self, arg, command):
        patterns = arg.split()
        supervisor = self.ctl.get_supervisor()
        for process in supervisor.getAllProcessInfo():
            print(process)
        self.ctl.output('No process matched given expression.')

    def _show_help(self, help, command):
        self.ctl.output('The same as %s, but accepts wildcard expressions to match the process name.' % command)
        self.ctl.output('m%s a* - %ss all processes begining with "a".' % (command, command))

    def do_cmstop(self, arg):
        supervisor = self.ctl.get_supervisor()
        import pdb; pdb.set_trace()
        result = supervisor.reloadConfig()

    def do_cmstart(self, arg):
        print('Starting celery multi')
        print(arg)
        import pdb; pdb.set_trace()

    def do_cmrestart(self, arg):
        self._expand_wildcards(arg, command='restart')

    def help_cmstop(self):
        return self._wrap_help('stop')

    def help_cmstart(self):
        help_text = """
        This is some help text for start command
        """
        return self._show_help(help_text, command='cmstart')

    def help_cmrestart(self):
        return self._wrap_help('restart')


def make_celerymulti_controllerplugin(controller, **config):
    return CeleryMultiControllerPlugin(controller, **config)
