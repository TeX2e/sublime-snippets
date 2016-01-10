
from __future__ import print_function
import sys

class Error(object):
    """docstring for Error"""
    @staticmethod
    def message(file_name, line_num, pos, message):
        return "%s:%d:%d: error: %s" % (file_name, line_num, pos, message)

    @staticmethod
    def print_error(message):
        print(message, file=sys.stderr)
