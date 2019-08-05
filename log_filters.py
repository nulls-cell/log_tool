# @Time    : 2019/7/16 11:03 AM
# @Author  : lirui
# @ qq     : 270239148
import logging


class NoDebugFilter(logging.Filter):

    def filter(self, record):
        return False


class DebugFilter(logging.Filter):

    def filter(self, record):
        return True


class InfoFilter(logging.Filter):

    def filter(self, record):
        level = record.levelname.upper()
        if level in {'INFO', 'WARNING', 'ERROR'}:
            return True
        return False


class WarningFilter(logging.Filter):

    def filter(self, record):
        level = record.levelname.upper()
        if level == 'WARNING':
            return True
        return False


class ErrorFilter(logging.Filter):

    def filter(self, record):
        level = record.levelname.upper()
        if level == 'ERROR':
            return True
        return False


class CriticalFilter(logging.Filter):

    def filter(self, record):
        level = record.levelname.upper()
        if level == 'CRITICAL':
            return True
        return False
