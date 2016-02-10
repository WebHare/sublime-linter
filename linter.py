#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Kris Breuker
# Copyright (c) 2015-2016 B-Lex IT B.V.
#
# License: MIT
#

"""This module exports the Hslint plugin class."""

import sublime
from SublimeLinter.lint import Linter, util
from WebHare.EditorSupport import EditorSupportCall, getViewStoredData


class Hslint(Linter):
    """Provides an interface to hslint."""

    syntax = 'harescript'
    cmd = None # No command, running inline
    executable = None # No executable, running inline
    version_args = '--version'
    version_re = r'(?P<version>\d+\.\d+\.\d+)'
    version_requirement = '>= 1.0'
    regex = (
        r'^(?:(?P<error>[E])|(?P<warning>[W])):'
        r'?:(?P<line>\d+):(?P<col>\d+):'
        r'(?P<message>.+)'
    )
    multiline = False
    line_col_base = (1, 1)
    tempfile_suffix = None
    error_stream = util.STREAM_BOTH
    selectors = {
        'harescript': 'source.harescript'
    }
    word_re = None
    defaults = {}
    inline_settings = None
    inline_overrides = None
    comment_re = r'\s*/[/*]'

    """Run the linter, return a string with one error/warning per line"""
    def run(self, cmd, code):

        data = getViewStoredData(self.view, True)
        if "supported" in data and not data["supported"]:
            return

        data["authorative"] = True

        caller = EditorSupportCall(self.view)
        result = caller.call("validateharescriptsource", code)

        lintresult = ""
        if result:
            if "errors" not in result and "warnings" not in result:
                # Display a message
                sublime.status_message("No validation results received")
                return

            if "supported" in result and not result["supported"]:
                sublime.status_message("Target server does not support validation")
                data["supported"] = False
                return

            lines = []
            messages = []

            if "errors" in result:
                for idx, obj in enumerate(result["errors"]):
                    if obj["line"] in lines: # One message per line
                        continue
                    if not obj["istopfile"]:
                        obj["line"] = 1
                        obj["col"] = 1

                    lines.append(obj["line"])
                    messages.append(obj)
                    lintresult += "E:" + str(obj["line"]) + ":" + str(obj["col"]) + ":" + obj["message"] + "\n"

            if "warnings" in result:
                for idx, obj in enumerate(result["warnings"]):
                    if obj["line"] in lines: # One message per line
                        continue
                    if not obj["istopfile"]:
                        obj["line"] = 1
                        obj["col"] = 1

                    lines.append(obj["line"])
                    messages.append(obj)
                    lintresult += "W:" + str(obj["line"]) + ":" + str(obj["col"]) + ":" + obj["message"] + "\n"

            data["messages"] = messages
        else:
            data["supported"] = False

        return lintresult
