import logging
import os

from hexagon import utils
from hexagon.constants import Lang


logger = logging.getLogger("hexagon.execute")


class Executor(object):

    def __init__(self, path, lang=None, args=None, timeout=None):
        super(Executor, self).__init__()
        self.path = utils.format_path(path)
        self.lang = utils.parse_lang(self.path) if lang is None else utils.format_lang(lang)
        self.args = args
        self.timeout = utils.first_not_none(timeout, utils.Global.timeout)

    def execute(self, stdin, stdout):
        try:
            logger.info(f"Execute {self.path}")
            with utils.FileContext(stdin, stdout) as context:
                return self._execute(context.stdin, context.stdout)
        except Exception as e:
            logger.error(str(e))

    def _execute(self, stdin, stdout):
        workdir = os.path.dirname(self.path)
        basename = os.path.basename(self.path)
        if self.lang == Lang.JAVA:
            if basename.endswith(".class"):
                basename = basename[:-6]
            cmd = ["java", basename]
        elif self.lang == Lang.PY:
            if basename.endswith(".py"):
                basename = basename[:-3]
            cmd = ["python", "-m", basename]
        else:
            cmd = [basename]
        if self.args:
            cmd.append(self.args)

        with utils.WorkdirContext(workdir):
            return utils.run_subprocess(cmd, self.timeout, stdin, stdout, None, logger) == 0, 0
