# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import logging
import sys

import click
import nsbl
from frkl import frkl

from . import print_version
from .commands import CommandRepo
from .freckles_defaults import *
from .utils import DEFAULT_FRECKLES_CONFIG, get_local_repos

log = logging.getLogger("freckles")

# TODO: this is a bit ugly, probably have refactor how role repos are used
nsbl.defaults.DEFAULT_ROLES_PATH = os.path.join(os.path.dirname(__file__), "external", "default_role_repo")
EXTRA_FRECKLES_PLUGINS = os.path.abspath(os.path.join(os.path.dirname(__file__), "external", "freckles_extra_plugins"))

FRECKLES_HELP_TEXT = """Executes a list of tasks specified in a (yaml-formated) text file (called a 'frecklecutable').

*frecklecute* comes with a few default frecklecutables that are used to manage itself (as well as its sister application *freckles*) as well as a few useful generic ones. Visit the online documentation for more details: https://docs.freckles.io/en/latest/frecklecute_command.html
"""
FRECKLES_EPILOG_TEXT = "frecklecute is free and open source software and part of the 'freckles' project, for more information visit: https://docs.freckles.io"

COMMAND_PROCESSOR_CHAIN = [
    frkl.UrlAbbrevProcessor()
]

# we need the current command to dynamically add it to the available ones
current_command = None

# temp_repo = CommandRepo(paths=[], additional_commands=[], no_run=True)
# command_list = temp_repo.get_commands().keys()

if sys.argv[0].endswith("frecklecute"):
    for arg in sys.argv[1:]:

        if arg.startswith("-"):
            continue

            # if arg in command_list:
            # current_command = None
            # current_command_path = None
            # break

        if os.path.exists(arg):
            current_command = arg
            current_command_path = os.path.abspath(arg)
            # frkl_obj = frkl.Frkl(current_command, COMMAND_PROCESSOR_CHAIN)
            # current_command = frkl_obj.process()[0]
            break

if not current_command:
    current_command = None
    current_command_path = None


class FrecklesCommand(click.MultiCommand):
    def __init__(self, current_command, command_repos=[], **kwargs):

        click.MultiCommand.__init__(self, "freckles", **kwargs)

        output_option = click.Option(param_decls=["--output", "-o"], required=False, default="default",
                                     metavar="FORMAT", type=click.Choice(SUPPORTED_OUTPUT_FORMATS),
                                     help="format of the output")
        ask_become_pass_option = click.Option(param_decls=["--ask-become-pass", "-pw"],
                                              help='whether to force ask for a password, force ask not to, or let try freckles decide (which might not always work)',
                                              type=click.Choice(["auto", "true", "false"]), default="auto")
        version_option = click.Option(param_decls=["--version"], help='prints the version of freckles', type=bool,
                                      is_flag=True, is_eager=True, expose_value=False, callback=print_version)
        no_run_option = click.Option(param_decls=["--no-run"],
                                     help='don\'t execute frecklecute, only prepare environment and print task list',
                                     type=bool, is_flag=True, default=False, required=False)

        self.params = [output_option, ask_become_pass_option, no_run_option, version_option]

        self.command_repo = CommandRepo(paths=command_repos, additional_commands=[current_command])
        self.current_command = current_command[0]
        self.command_names = self.command_repo.commands.keys()
        self.command_names.sort()
        if self.current_command:
            self.command_names.insert(0, self.current_command)

        self.commands = {}
        for name in self.command_names:
            self.commands[name] = self.get_command(None, name)

    def list_commands(self, ctx):

        return self.command_names

    def get_command(self, ctx, name):

        if name in self.command_repo.commands.keys():
            return self.command_repo.get_command(ctx, name)

        else:
            return None


click.core.SUBCOMMAND_METAVAR = 'FRECKLECUTABLE [ARGS]...'
click.core.SUBCOMMANDS_METAVAR = 'FRECKLECUTABLE1 [ARGS]... [FRECKLECUTABLE2 [ARGS]...]...'

trusted_repos = DEFAULT_FRECKLES_CONFIG.trusted_repos

local_paths = get_local_repos(trusted_repos, "frecklecutables")

cli = FrecklesCommand((current_command, current_command_path), command_repos=local_paths, help=FRECKLES_HELP_TEXT,
                      epilog=FRECKLES_EPILOG_TEXT)

if __name__ == "__main__":
    cli()
