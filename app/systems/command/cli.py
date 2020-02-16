from django.conf import settings
from django.db import connection
from django.core.management import call_command
from django.core.management.color import color_style, no_style
from django.core.management.base import CommandError, CommandParser

from systems.command.registry import CommandRegistry
from utility.runtime import Runtime
from utility.terminal import TerminalMixin
from utility.display import format_exception_info

import django
import os
import sys
import re
import time


class CLI(TerminalMixin):

    def __init__(self, argv):
        super().__init__()
        self.argv = argv
        self.registry = CommandRegistry()


    def handle_error(self, error):
        if not isinstance(error, CommandError):
            self.print()
            self.print('** ' + self.error_color(error.args[0]), sys.stderr)
            if Runtime.debug():
                self.print()
                self.print('> ' + self.traceback_color(
                        "\n".join([ item.strip() for item in format_exception_info() ])
                    ),
                    stream = sys.stderr
                )


    def initialize(self):
        django.setup()

        parser = CommandParser(add_help = False, allow_abbrev = False)
        parser.add_argument('args', nargs = '*')
        namespace, extra = parser.parse_known_args(self.argv[1:])
        args = namespace.args

        if not args:
            args = ['help']

        if not settings.NO_MIGRATE and args and args[0] not in ('migrate', 'makemigrations'):
            mutex_file = "{}/migrate.lock".format(settings.LOCK_BASE_PATH)

            if not os.path.exists(mutex_file):
                open(mutex_file, 'a').close()
                try:
                    call_command('migrate', interactive = False, verbosity = 0)
                    call_command('createcachetable', verbosity = 0)
                finally:
                    os.remove(mutex_file)
            else:
                while True:
                    if not os.path.exists(mutex_file):
                        break

                    self.print(self.notice_color("Waiting for migrate lock..."))
                    time.sleep(2)

        if '--debug' in extra:
            Runtime.debug(True)

        if '--no-color' in extra:
            Runtime.color(False)

        return args

    def execute(self):
        try:
            try:
                self.registry.find_command(
                    self.initialize(),
                    main = True
                ).run_from_argv(self.argv)
                self.exit(0)

            except KeyboardInterrupt:
                self.print(
                    '> ' + self.error_color('User aborted'),
                    stream = sys.stderr
                )
            except Exception as e:
                self.handle_error(e)

            self.exit(1)
        finally:
            connection.close()


def execute(argv):
    CLI(argv).execute()
