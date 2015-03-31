#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Aparajita Fishman
# Copyright (c) 2014 Aparajita Fishman
#
# License: MIT
#

"""This module exports the Xmllint plugin class."""

from SublimeLinter.lint import Linter, util, persist
from xml.dom import minidom
import os


class Xmllint(Linter):

    """Provides an interface to xmllint."""

    syntax = 'xml'
    executable = 'xmllint'
    regex = (
        r'^.+?:'
        r'(?P<line>\d+):.+?: '
        r'(?P<message>[^\r\n]+)\r?\n'
        r'(?:[^\r\n]*\r?\n)?'
        r'(?:(?P<col>[^\^]*)\^)?'
    )
    multiline = True
    error_stream = util.STREAM_STDERR

    def run(self, cmd, code):
        if not self.schema_exists:
            # TODO: Replace 1 with correct line
            return '-:1: schema error : Schema file does not exist\n'

        return super().run(cmd, code)

    def cmd(self):
        """Return a list with the command line to execute."""

        result = [self.executable_path, '--noout', '*']

        if self.filename:
            schema = self.schema_path()

            if schema:
                result.append('--schema')
                result.append(schema)

        result.append('-')

        return result

    def schema_path(self):
        self.schema_exists = True
        try:
            xsi = 'http://www.w3.org/2001/XMLSchema-instance'
            root = minidom.parseString(self.code).documentElement
            schema = root.getAttributeNS(xsi, 'noNamespaceSchemaLocation')

            if schema:
                online = schema.find('http://') == 0 or schema.find('https://') == 0
                if not (online or os.path.isabs(schema)):
                    schema = os.path.dirname(self.filename) + '/' + schema

                if not online and not os.path.isfile(schema):
                    self.schema_exists = False
                    return None

                return schema
        except Exception as e:
            persist.debug(e)

        return None
