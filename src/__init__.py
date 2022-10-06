import logging
import os
from subprocess import PIPE
from subprocess import Popen
from typing import Tuple

from src.version import __version__  # noqa

logger = logging.getLogger(__name__)


def create_process(cmd):
    process = Popen(
        [cmd], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True, preexec_fn=os.setsid
    )
    return process


def break_path(file_path: str) -> Tuple[str, str, str]:
    path_name, ext = os.path.splitext(file_path)
    fpath = os.path.dirname(path_name)
    fname = os.path.basename(path_name)

    return fpath, fname, ext
