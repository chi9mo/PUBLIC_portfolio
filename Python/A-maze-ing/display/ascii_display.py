"""ASCII terminal display for maze visualization.

Renders the maze using box-drawing characters with ANSI colour
support. Provides interactive controls for re-generation, path
toggle, and colour changes.
"""

import select
import sys
import time
import termios
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set

from mazegen.generator import (
    NORTH, EAST, SOUTH, WEST,
)
from display import MazeContext, disable_term_signals
from display.anim import (
    full_animate_gen, animate_solve_steps,
    finalize_generation,
)

# Cycle lists for interactive config changes
_ALGORITHMS: list[str] = [
    "recursive_backtracker", "kruskal", "prim",
]
_SOLVERS: list[str] = ["bfs", "bibfs", "astar"]

# ANSI escape helpers
_HIDE_CUR: str = "\033[?25l"
_SHOW_CUR: str = "\033[?25h"
_ALT_ON: str = "\033[?1049h"
_ALT_OFF: str = "\033[?1049l"
_HOME: str = "\033[H"
_CLEAR_DOWN: str = "\033[J"
_CLEAR_LINE: str = "\033[K"

# ANSI colour codes for walls
COLOUR_PRESETS: List[Tuple[str, str]] = [
    ("White", "\033[97m"),
    ("Green", "\033[92m"),
    ("Cyan", "\033[96m"),
    ("Yellow", "\033[93m"),
    ("Magenta", "\033[95m"),
    ("Red", "\033[91m"),
]

RESET: str = "\033[0m"
PATH_COLOUR: str = "\033[93m"
ENTRY_COLOUR: str = "\033[92m"
EXIT_COLOUR: str = "\033[91m"
EXPLORED_COLOUR: str = "\033[96m"

PATTERN_COLOUR_PRESETS: List[Tuple[str, str]] = [
    ("Blue", "\033[94m"),
    ("Cyan", "\033[96m"),
    ("Magenta", "\033[95m"),
    ("Yellow", "\033[93m"),
    ("Red", "\033[91m"),
    ("White", "\033[97m"),
]


@dataclass
class RenderOptions:
    """Options for ASCII maze rendering."""

    path_str: str = ""
    show_path: bool = True
    wall_colour_idx: int = 0
    pattern_cells: Optional[Set[Tuple[int, int]]] = None
    pattern_colour_idx: int = 0
    explored_cells: Optional[Set[Tuple[int, int]]] = None


@dataclass
class _InteractiveState:
    """Mutable state for the interactive ASCII loop."""

    show_path: bool
    colour_idx: int
    pat_colour_idx: int
    current_seed: Optional[int]
    current_path: str
    pattern_cells: Set[Tuple[int, int]]
    solver: str


@dataclass
class _CellSets:
    """Cell overlay data for rendering."""

    entry: Tuple[int, int]
    exit_pos: Tuple[int, int]
    pat: Set[Tuple[int, int]]
    pat_idx: int
    path_set: Set[Tuple[int, int]]
    expl: Set[Tuple[int, int]]


# ---- Rendering ------------------------------------------

def render_ascii(
    ctx: MazeContext,
    opts: RenderOptions,
) -> str:
    """Render the maze as an ASCII string."""
    maze = ctx.maze
    entry = ctx.entry
    exit_pos = ctx.exit_pos
    w, h = maze.width, maze.height
    grid = maze.grid
    wc = COLOUR_PRESETS[
        opts.wall_colour_idx % len(COLOUR_PRESETS)
    ][1]

    path_set = (
        _path_to_cells(entry, opts.path_str)
        if opts.show_path and opts.path_str else set()
    )
    cs = _CellSets(
        entry, exit_pos,
        opts.pattern_cells or set(),
        opts.pattern_colour_idx,
        path_set,
        opts.explored_cells or set(),
    )

    lines: List[str] = [_top_border(grid, w, wc)]
    for y in range(h):
        lines.append(_cell_row(grid, y, w, wc, cs))
        lines.append(_bottom_border(grid, y, w, wc))
    return "\n".join(lines)


def _top_border(
    grid: List[List[int]], w: int, wc: str,
) -> str:
    top = wc + "+"
    for x in range(w):
        top += "---+" if grid[0][x] & NORTH else "   +"
    return top + RESET


def _bottom_border(
    grid: List[List[int]], y: int, w: int, wc: str,
) -> str:
    bot = wc + "+"
    for x in range(w):
        bot += "---+" if grid[y][x] & SOUTH else "   +"
    return bot + RESET


def _cell_row(
    grid: List[List[int]],
    y: int, w: int, wc: str,
    cs: _CellSets,
) -> str:
    row = ""
    for x in range(w):
        if not x:
            row += (
                wc + "|" + RESET
                if grid[y][x] & WEST else " "
            )
        row += _cell_content(x, y, cs)
        row += (
            wc + "|" + RESET
            if grid[y][x] & EAST else " "
        )
    return row


def _cell_content(
    x: int, y: int, cs: _CellSets,
) -> str:
    if (x, y) == cs.entry:
        return ENTRY_COLOUR + " E " + RESET
    if (x, y) == cs.exit_pos:
        return EXIT_COLOUR + " X " + RESET
    if (x, y) in cs.pat:
        pc = PATTERN_COLOUR_PRESETS[
            cs.pat_idx % len(PATTERN_COLOUR_PRESETS)
        ][1]
        return pc + "\u2588\u2588\u2588" + RESET
    if (x, y) in cs.path_set:
        return PATH_COLOUR + " \u00b7 " + RESET
    if (x, y) in cs.expl:
        return EXPLORED_COLOUR + " \u00b7 " + RESET
    return "   "


# ---- Helpers --------------------------------------------

def _path_to_cells(
    start: Tuple[int, int], path_str: str,
) -> Set[Tuple[int, int]]:
    """Convert a path string to a set of (x, y) cells."""
    cells: Set[Tuple[int, int]] = {start}
    x, y = start
    dm = {"N": (0, -1), "E": (1, 0),
          "S": (0, 1), "W": (-1, 0)}
    for ch in path_str:
        dx, dy = dm.get(ch, (0, 0))
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells


def _refresh(text: str) -> None:
    """Overwrite the screen with text in place."""
    cleaned = text.replace("\n", _CLEAR_LINE + "\n")
    sys.stdout.write(_HOME + cleaned + _CLEAR_DOWN)
    sys.stdout.flush()


def _getch() -> str:
    """Read a single keypress without requiring Enter."""
    ch = sys.stdin.read(1)
    if not ch:
        raise EOFError
    if ch == "\x1b":
        nxt = sys.stdin.read(1)
        if nxt == "[":
            while True:
                c = sys.stdin.read(1)
                if not c or c.isalpha() or c == "~":
                    break
        return ""
    return ch


def _check_stdin_interrupt() -> bool:
    """Non-blocking check for Ctrl+C on stdin."""
    rlist, _, _ = select.select([sys.stdin], [], [], 0)
    if rlist:
        ch = sys.stdin.read(1)
        return ch == "\x03"
    return False


# ---- Interactive display --------------------------------

def interactive_ascii(
    ctx: MazeContext,
    path_str: str,
    seed: Optional[int],
    solver: str = "bfs",
) -> None:
    """Run interactive ASCII display loop."""
    state = _InteractiveState(
        show_path=True, colour_idx=0, pat_colour_idx=0,
        current_seed=seed, current_path=path_str,
        pattern_cells=set(ctx.maze.pattern_cells),
        solver=solver,
    )
    fd, old_attrs = disable_term_signals(
        clear_iexten=True, vmin=1, vtime=0,
    )
    sys.stdout.write(_ALT_ON + _HIDE_CUR)
    sys.stdout.flush()
    try:
        _interactive_loop(ctx, state)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_attrs)
        sys.stdout.write(_SHOW_CUR + _ALT_OFF)
        sys.stdout.flush()


def _interactive_loop(
    ctx: MazeContext, st: _InteractiveState,
) -> None:
    """Inner interactive loop."""
    while True:
        try:
            _draw_frame(ctx, st)
            choice = _getch().lower()
        except EOFError:
            break
        if choice in ("q", "\x03"):
            break
        _handle_key(ctx, st, choice)


def _draw_frame(
    ctx: MazeContext, st: _InteractiveState,
) -> None:
    """Render and display current state."""
    output = render_ascii(
        ctx, RenderOptions(
            st.current_path, st.show_path,
            st.colour_idx, st.pattern_cells,
            st.pat_colour_idx,
        ),
    )
    cn = COLOUR_PRESETS[
        st.colour_idx % len(COLOUR_PRESETS)
    ][0]
    pn = PATTERN_COLOUR_PRESETS[
        st.pat_colour_idx % len(PATTERN_COLOUR_PRESETS)
    ][0]
    pl = "on" if st.show_path else "off"
    maze = ctx.maze
    frame = (
        output + "\n"
        f"\nSeed: {st.current_seed} | "
        f"Algo: {maze.algorithm} | "
        f"Solver: {st.solver} | "
        f"Perfect: {'yes' if maze.perfect else 'no'}\n"
        f"Walls: {cn} | 42: {pn} | Path: {pl}\n"
        f"\n[r]Regen [p]Path [c]Colour "
        f"[t]42col [s]Seed\n"
        f"[g]Algo [f]Solver [x]Perfect "
        f"[a]Anim [v]Solve [q]Quit\n"
    )
    _refresh(frame)


def _handle_key(
    ctx: MazeContext, st: _InteractiveState,
    choice: str,
) -> None:
    """Process a single keypress."""
    maze = ctx.maze
    if choice == "r":
        _regen(ctx, st)
    elif choice == "p":
        st.show_path = not st.show_path
    elif choice == "c":
        st.colour_idx = (
            (st.colour_idx + 1) % len(COLOUR_PRESETS)
        )
    elif choice == "t":
        st.pat_colour_idx = (
            (st.pat_colour_idx + 1)
            % len(PATTERN_COLOUR_PRESETS)
        )
    elif choice == "s":
        _handle_seed_input(ctx, st)
    elif choice == "g":
        _cycle_algorithm(ctx, st)
    elif choice == "f":
        _cycle_solver(ctx, st)
    elif choice == "x":
        _toggle_perfect(ctx, st)
    elif choice == "a":
        maze.seed = st.current_seed
        st.current_path = animate_generation(
            ctx, st.colour_idx, st.pat_colour_idx,
            st.solver,
        )
        st.pattern_cells = set(maze.pattern_cells)
    elif choice == "v":
        st.current_path = animate_solve(
            ctx, st.colour_idx, st.pat_colour_idx,
            st.solver,
        )
        st.show_path = True


def _regen(
    ctx: MazeContext, st: _InteractiveState,
) -> None:
    """Regenerate maze with incremented seed."""
    if st.current_seed is not None:
        st.current_seed += 1
    else:
        st.current_seed = int(time.time())
    ctx.maze.seed = st.current_seed
    _rebuild(ctx, st)


def _rebuild(
    ctx: MazeContext, st: _InteractiveState,
) -> None:
    """Regenerate maze, place pattern, solve."""
    ctx.maze.generate()
    st.current_path = finalize_generation(ctx, st.solver)
    st.pattern_cells = set(ctx.maze.pattern_cells)


def _handle_seed_input(
    ctx: MazeContext, st: _InteractiveState,
) -> None:
    """Prompt for seed and regenerate."""
    buf = ""
    while True:
        _refresh_seed_prompt(ctx, st, buf)
        ch = sys.stdin.read(1)
        if not ch:
            return
        if ch in ("\x03", "\x1b"):
            return
        if ch in ("\r", "\n"):
            if not buf or buf == "-":
                return
            st.current_seed = int(buf)
            ctx.maze.seed = st.current_seed
            _rebuild(ctx, st)
            return
        if ch in ("\x7f", "\x08"):
            buf = buf[:-1]
        elif ch == "-" and not buf:
            buf = "-"
        elif "0" <= ch <= "9":
            buf += ch


def _refresh_seed_prompt(
    ctx: MazeContext, st: _InteractiveState,
    buf: str,
) -> None:
    """Redraw the frame with a seed input prompt."""
    output = render_ascii(
        ctx, RenderOptions(
            st.current_path, st.show_path,
            st.colour_idx, st.pattern_cells,
            st.pat_colour_idx,
        ),
    )
    frame = output + f"\n\nSeed> {buf}_\n"
    _refresh(frame)


def _cycle_algorithm(
    ctx: MazeContext, st: _InteractiveState,
) -> None:
    """Cycle to next generation algorithm."""
    maze = ctx.maze
    ai = _ALGORITHMS.index(maze.algorithm)
    maze.algorithm = _ALGORITHMS[
        (ai + 1) % len(_ALGORITHMS)
    ]
    _rebuild(ctx, st)


def _cycle_solver(
    ctx: MazeContext, st: _InteractiveState,
) -> None:
    """Cycle to next solver."""
    fi = _SOLVERS.index(st.solver)
    st.solver = _SOLVERS[(fi + 1) % len(_SOLVERS)]
    try:
        st.current_path = ctx.maze.solve(
            ctx.entry, ctx.exit_pos, solver=st.solver,
        )
    except ValueError:
        st.current_path = ""


def _toggle_perfect(
    ctx: MazeContext, st: _InteractiveState,
) -> None:
    """Toggle perfect mode and regenerate."""
    ctx.maze.perfect = not ctx.maze.perfect
    _rebuild(ctx, st)


# ---- Animation ------------------------------------------

def animate_generation(
    ctx: MazeContext,
    wall_colour_idx: int = 0,
    pattern_colour_idx: int = 0,
    solver: str = "bfs",
) -> str:
    """Animate maze generation step by step."""
    maze = ctx.maze
    iv = max(1, (maze.width * maze.height) // 60)
    stop_flag = [False]

    def _should_stop() -> bool:
        if stop_flag[0]:
            return True
        if _check_stdin_interrupt():
            stop_flag[0] = True
            return True
        return False

    def on_step(step: int) -> None:
        if not step % iv:
            out = render_ascii(
                ctx, RenderOptions(
                    show_path=False,
                    wall_colour_idx=wall_colour_idx,
                    pattern_colour_idx=pattern_colour_idx,
                ),
            )
            _refresh(
                out + "\n"
                f"\nGenerating ({maze.algorithm})...\n"
            )
            time.sleep(0.03)

    path = full_animate_gen(
        ctx, on_step, solver,
        should_stop=_should_stop,
    )

    done = render_ascii(
        ctx, RenderOptions(
            path_str=path,
            wall_colour_idx=wall_colour_idx,
            pattern_cells=set(maze.pattern_cells),
            pattern_colour_idx=pattern_colour_idx,
        ),
    )
    _refresh(done + "\n\nGeneration complete!\n")
    return path


def animate_solve(
    ctx: MazeContext,
    wall_colour_idx: int = 0,
    pattern_colour_idx: int = 0,
    solver: str = "bfs",
) -> str:
    """Animate solving step-by-step."""
    maze = ctx.maze
    iv = max(1, (maze.width * maze.height) // 40)
    solver_label = {
        "bfs": "BFS", "bibfs": "BiBFS", "astar": "A*",
    }.get(solver, solver)
    stop_flag = [False]

    def _should_stop() -> bool:
        if stop_flag[0]:
            return True
        if _check_stdin_interrupt():
            stop_flag[0] = True
            return True
        return False

    def on_step(
        step: int, explored: Set[Tuple[int, int]],
    ) -> None:
        if not step % iv:
            out = render_ascii(
                ctx, RenderOptions(
                    show_path=False,
                    wall_colour_idx=wall_colour_idx,
                    pattern_cells=set(maze.pattern_cells),
                    pattern_colour_idx=pattern_colour_idx,
                    explored_cells=explored,
                ),
            )
            _refresh(
                out + "\n"
                f"\nSolving ({solver_label})... "
                f"({len(explored)} explored)\n"
            )
            time.sleep(0.02)

    result = animate_solve_steps(
        maze, (ctx.entry, ctx.exit_pos), solver,
        on_step=on_step,
        should_stop=_should_stop,
    )
    path = result or ""

    final = render_ascii(
        ctx, RenderOptions(
            path_str=path,
            wall_colour_idx=wall_colour_idx,
            pattern_cells=set(maze.pattern_cells),
            pattern_colour_idx=pattern_colour_idx,
        ),
    )
    _refresh(
        final + "\n"
        f"\nSolved! Path length: {len(path)}\n"
    )
    return path
