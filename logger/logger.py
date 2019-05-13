import sys
import traceback


class logger:
    """ Logsystem """

    def __init__(self):
        self.exc_type,  self.exc_value,  self.exc_traceback = sys.exc_info()

    def error(self):
        traceback.print_exception(self.exc_type,  self.exc_value,  self.exc_traceback, limit=2, file=sys.stdout)

    @staticmethod
    def warning(message):
        print(message)
