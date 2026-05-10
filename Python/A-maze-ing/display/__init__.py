"""Display package for A-Maze-ing project."""

import sys
import termios
from dataclasses import dataclass
from typing import Tuple, Any

from mazegen.generator import MazeGenerator


@dataclass
class MazeContext:
    """Bundle maze instance with entry/exit coordinates."""

    maze: MazeGenerator
    entry: Tuple[int, int]
    exit_pos: Tuple[int, int]


def disable_term_signals(
    *, clear_echo: bool = True,
    clear_icanon: bool = True,
    clear_iexten: bool = False,
    vmin: int = 1, vtime: int = 0,
) -> Tuple[int, Any]:
    """Disable ISIG (and optionally other lflag bits) on stdin.

    Returns (fd, old_attrs) so the caller can restore later
    via ``termios.tcsetattr(fd, termios.TCSADRAIN, old_attrs)``.
    """
    fd = sys.stdin.fileno()
    old_attrs: Any = termios.tcgetattr(fd)
    new_attrs: Any = termios.tcgetattr(fd)
    mask = termios.ISIG
    if clear_echo:
        mask |= termios.ECHO
    if clear_icanon:
        mask |= termios.ICANON
    if clear_iexten:
        mask |= termios.IEXTEN
    new_attrs[3] = new_attrs[3] & ~mask
    new_attrs[6][termios.VMIN] = vmin
    new_attrs[6][termios.VTIME] = vtime
    termios.tcsetattr(fd, termios.TCSADRAIN, new_attrs)
    return fd, old_attrs
