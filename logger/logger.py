import sys
import traceback
import config as cfg


class logger:
    """ Logsystem """

    def __init__(self):
        self.exc_type,  self.exc_value,  self.exc_traceback = sys.exc_info()

    def error(self):
        if cfg.debug:
            traceback.print_exception(self.exc_type,  self.exc_value,  self.exc_traceback, limit=2, file=sys.stdout)

    @staticmethod
    def warning(message):
        if cfg.debug:
            print(message)
