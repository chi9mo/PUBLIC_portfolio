"""MLX graphical display for maze visualization.

Single full-window image per frame — no flicker.
Text rendered via built-in bitmap font at 1.5x scale.

Key bindings:
    r - Regenerate   p - Toggle path   c - Cycle colour
    a - Animate gen  v - Animate solve q/Esc - Quit
"""

import importlib
import select
import sys
import termios
import time
import types
from dataclasses import dataclass, field
from typing import Tuple, Set, Optional, Any

from mazegen.generator import (
    NORTH, EAST, SOUTH, WEST, ALL_WALLS,
    create_rng,
)
from display import MazeContext, disable_term_signals
from display.anim import (
    animate_gen_steps, animate_solve_steps,
    finalize_generation,
)

_MLX_MOD: Optional[types.ModuleType] = None
try:
    _MLX_MOD = importlib.import_module("mlx")
except ImportError:
    pass

MLX_AVAILABLE: bool = _MLX_MOD is not None

_ALGORITHMS: list[str] = [
    "recursive_backtracker", "kruskal", "prim",
]
_SOLVERS: list[str] = ["bfs", "bibfs", "astar"]

CELL: int = 20
WALL: int = 2
PAD: int = 40

COLOURS: list[Tuple[str, int]] = [
    ("White", 0xFFFFFF), ("Green", 0x00FF00),
    ("Cyan", 0x00FFFF), ("Yellow", 0xFFFF00),
    ("Magenta", 0xFF00FF), ("Red", 0xFF0000),
]
BG: int = 0x1A1A2E
COL_PATH: int = 0xFFD700
COL_ENTRY: int = 0x00FF00
COL_EXIT: int = 0xFF4444
COL_EXPLORED: int = 0x00CCCC
COL_TEXT: int = 0xAAAAAA
COL_HELP: int = 0x666666

PAT_COLOURS: list[Tuple[str, int]] = [
    ("Blue", 0x4488FF), ("Cyan", 0x00FFFF),
    ("Magenta", 0xFF00FF), ("Yellow", 0xFFFF00),
    ("Red", 0xFF4444), ("White", 0xFFFFFF),
]

_GLYPH: dict[str, list[int]] = {}
_GW: int = 8
_CW: int = 9
_CH: int = 18


def _init_font() -> None:
    """Populate _GLYPH with 5x7 bitmaps for ASCII."""
    g: dict[str, list[int]] = {
        ' ': [0]*7,
        '0': [0xe, 0x11, 0x13, 0x15, 0x19, 0x11, 0xe],
        '1': [0x4, 0xc, 0x4, 0x4, 0x4, 0x4, 0xe],
        '2': [0xe, 0x11, 0x1, 0x2, 0x4, 0x8, 0x1f],
        '3': [0x1f, 0x2, 0x4, 0xe, 0x1, 0x11, 0xe],
        '4': [0x2, 0x6, 0xa, 0x12, 0x1f, 0x2, 0x2],
        '5': [0x1f, 0x10, 0x1e, 0x1, 0x1, 0x11, 0xe],
        '6': [0x6, 0x8, 0x10, 0x1e, 0x11, 0x11, 0xe],
        '7': [0x1f, 0x1, 0x2, 0x4, 0x8, 0x8, 0x8],
        '8': [0xe, 0x11, 0x11, 0xe, 0x11, 0x11, 0xe],
        '9': [0xe, 0x11, 0x11, 0xf, 0x1, 0x2, 0xc],
        'A': [0xe, 0x11, 0x11, 0x1f, 0x11, 0x11, 0x11],
        'B': [0x1e, 0x11, 0x11, 0x1e, 0x11, 0x11, 0x1e],
        'C': [0xe, 0x11, 0x10, 0x10, 0x10, 0x11, 0xe],
        'D': [0x1c, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1c],
        'E': [0x1f, 0x10, 0x10, 0x1e, 0x10, 0x10, 0x1f],
        'F': [0x1f, 0x10, 0x10, 0x1e, 0x10, 0x10, 0x10],
        'G': [0xe, 0x11, 0x10, 0x17, 0x11, 0x11, 0xe],
        'H': [0x11, 0x11, 0x11, 0x1f, 0x11, 0x11, 0x11],
        'I': [0xe, 0x4, 0x4, 0x4, 0x4, 0x4, 0xe],
        'J': [0x7, 0x2, 0x2, 0x2, 0x2, 0x12, 0xc],
        'K': [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
        'L': [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1f],
        'M': [0x11, 0x1b, 0x15, 0x15, 0x11, 0x11, 0x11],
        'N': [0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11],
        'O': [0xe, 0x11, 0x11, 0x11, 0x11, 0x11, 0xe],
        'P': [0x1e, 0x11, 0x11, 0x1e, 0x10, 0x10, 0x10],
        'Q': [0xe, 0x11, 0x11, 0x11, 0x15, 0x12, 0xd],
        'R': [0x1e, 0x11, 0x11, 0x1e, 0x14, 0x12, 0x11],
        'S': [0xf, 0x10, 0x10, 0xe, 0x1, 0x1, 0x1e],
        'T': [0x1f, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4],
        'U': [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0xe],
        'V': [0x11, 0x11, 0x11, 0x11, 0xa, 0xa, 0x4],
        'W': [0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0xa],
        'X': [0x11, 0x11, 0xa, 0x4, 0xa, 0x11, 0x11],
        'Y': [0x11, 0x11, 0xa, 0x4, 0x4, 0x4, 0x4],
        'Z': [0x1f, 0x1, 0x2, 0x4, 0x8, 0x10, 0x1f],
        ':': [0, 0, 0x4, 0, 0x4, 0, 0],
        '.': [0, 0, 0, 0, 0, 0, 0x4],
        ',': [0, 0, 0, 0, 0, 0x4, 0x8],
        '-': [0, 0, 0, 0xe, 0, 0, 0],
        '_': [0, 0, 0, 0, 0, 0, 0x1f],
        '/': [0, 0x1, 0x2, 0x4, 0x8, 0x10, 0],
        '(': [0x2, 0x4, 0x8, 0x8, 0x8, 0x4, 0x2],
        ')': [0x8, 0x4, 0x2, 0x2, 0x2, 0x4, 0x8],
    }
    for ch, bits in list(g.items()):
        _GLYPH[ch] = bits
        if 'A' <= ch <= 'Z':
            _GLYPH[ch.lower()] = bits


_init_font()
_BLANK: list[int] = [0] * 7


@dataclass
class ImageBuffer:
    """MLX image pixel buffer."""

    data: Any
    stride: int
    bpp: int


def _put_text(
    buf: ImageBuffer, *,
    pos: Tuple[int, int], text: str,
    col: int, lim: int,
) -> None:
    """Render text into image buffer at 1.5x scale."""
    sx, sy = pos
    cb, cg, cr = col & 0xFF, (col >> 8) & 0xFF, (col >> 16) & 0xFF
    cx = sx
    for ch in text:
        if cx + _GW > lim:
            break
        bits = _GLYPH.get(ch, _BLANK)
        _render_glyph(buf, cx, sy, bits, (cb, cg, cr))
        cx += _CW


_COL_W = [2,  1,  2,  1,  2]
_ROW_H = [2,  1,  2,  1,  2,  1,  2]


def _render_glyph(
    buf: ImageBuffer,
    cx: int, sy: int,
    bits: list[int],
    rgb: Tuple[int, int, int],
) -> None:
    """Render one glyph into the image buffer."""
    dy = 0
    for br, rh in enumerate(_ROW_H):
        bv = bits[br]
        dx = 0
        for bc, cw in enumerate(_COL_W):
            if not bv & (0x10 >> bc):
                dx += cw
                continue
            for ry in range(rh):
                for rx in range(cw):
                    _set_pixel(
                        buf,
                        (sy+dy+ry) * buf.stride
                        + (cx+dx+rx) * buf.bpp,
                        rgb,
                    )
            dx += cw
        dy += rh


def _set_pixel(
    buf: ImageBuffer, offset: int,
    rgb: Tuple[int, int, int],
) -> None:
    """Write one RGBA pixel at the given byte offset."""
    buf.data[offset] = rgb[0]
    buf.data[offset + 1] = rgb[1]
    buf.data[offset + 2] = rgb[2]
    buf.data[offset + 3] = 0xFF


def _path_set(
    entry: Tuple[int, int], path: str,
) -> Set[Tuple[int, int]]:
    """Convert path string to set of visited cells."""
    cells: Set[Tuple[int, int]] = {entry}
    x, y = entry
    dm = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
    for c in path:
        dx, dy = dm.get(c, (0, 0))
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells


def _fill(
    buf: ImageBuffer, *,
    pos: Tuple[int, int],
    size: Tuple[int, int],
    col: int,
) -> None:
    """Fill a rectangle in the MLX image buffer."""
    x, y = pos
    w, h = size
    rgb = (col & 0xFF, (col >> 8) & 0xFF, (col >> 16) & 0xFF)
    for fy in range(h):
        for fx in range(w):
            _set_pixel(
                buf,
                (y + fy) * buf.stride + (x + fx) * buf.bpp,
                rgb,
            )


# ---- Data types ------------------------------------------

@dataclass
class _Dims:
    """Window dimensions."""

    mw: int
    mh: int
    win_w: int
    win_h: int


@dataclass
class _SeedInput:
    """Seed input mode state."""

    active: bool = False
    buf: str = ""


@dataclass
class _MlxState:
    """Mutable MLX state."""

    seed: Optional[int]
    path: str
    solver: str
    colours: list[int] = field(
        default_factory=lambda: [0,  0],
    )
    flags: list[bool] = field(
        default_factory=lambda: [True, False],
    )
    explored: Set[Tuple[int, int]] = field(
        default_factory=set,
    )
    seed_input: _SeedInput = field(
        default_factory=_SeedInput,
    )

    @property
    def show_path(self) -> bool:
        """Whether to show the path."""
        return self.flags[0]

    @show_path.setter
    def show_path(self, val: bool) -> None:
        self.flags[0] = val

    @property
    def quit_flag(self) -> bool:
        """Whether quit has been requested."""
        return self.flags[1]

    @quit_flag.setter
    def quit_flag(self, val: bool) -> None:
        self.flags[1] = val


@dataclass
class _CellOverlay:
    """Cell rendering overlay data."""

    entry: Tuple[int, int]
    exit_pos: Tuple[int, int]
    pat: Set[Tuple[int, int]]
    pat_c: int
    pc: Set[Tuple[int, int]]
    explored: Set[Tuple[int, int]]


# ---- Entry point -----------------------------------------

def run_mlx_display(
    ctx: MazeContext,
    path_str: str,
    seed: Optional[int],
    solver: str = "bfs",
) -> None:
    """Launch the MLX display."""
    if _MLX_MOD is None:
        raise RuntimeError("MLX library is not available")
    dims = _calc_dimensions(ctx.maze, seed, solver)
    state = _MlxState(seed, path_str, solver)
    _run_loop(ctx, dims, state)


def _calc_dimensions(
    maze: Any, seed: Any, solver: str,
) -> _Dims:
    mw = maze.width * CELL + WALL
    mh = maze.height * CELL + WALL
    txt_h = 5 * _CH + 10
    pf = "yes" if maze.perfect else "no"
    lines = [
        f"Seed:{seed}  Algo:{maze.algorithm}",
        f"Solver:{solver}  Perfect:{pf}",
        "Walls:Magenta  42:Magenta  Path:off",
        "R:Regen P:Path C:Col S:Seed G:Algo",
        "F:Solver X:Perf A:Anim V:Solve Q:Quit",
    ]
    max_txt = max(len(s) for s in lines) * _CW
    win_w = max(PAD + mw + PAD, max_txt + 2 * PAD)
    win_h = PAD + mh + PAD + txt_h
    return _Dims(mw, mh, win_w, win_h)


# ---- MLX loop -------------------------------------------

def _run_loop(
    ctx: MazeContext, dims: _Dims, st: _MlxState,
) -> None:
    """Set up MLX window and enter event loop."""
    if _MLX_MOD is None:
        raise RuntimeError("MLX library is not available")
    maze = ctx.maze
    m: Any = _MLX_MOD.Mlx()
    ptr = m.mlx_init()
    win = m.mlx_new_window(
        ptr, dims.win_w, dims.win_h, "A-Maze-ing",
    )
    cur: list[Any] = [None]

    def redraw() -> None:
        old = cur[0]
        cur[0] = _build_frame((m, ptr, win), ctx, dims, st)
        if old is not None:
            m.mlx_destroy_image(ptr, old)

    def rebuild() -> None:
        maze.generate()
        st.path = finalize_generation(ctx, st.solver)
        redraw()

    def on_key(kc: int, _p: Any) -> None:
        _handle_mlx_key(
            kc, ctx, st,
            (lambda: m.mlx_loop_exit(ptr), redraw, rebuild),
        )

    redraw()
    m.mlx_key_hook(win, on_key, None)
    m.mlx_hook(win, 17, 0, lambda _p: m.mlx_loop_exit(ptr), None)
    m.mlx_hook(win, 33, 0, lambda _p: m.mlx_loop_exit(ptr), None)

    def on_loop(_p: Any) -> None:
        if st.quit_flag:
            m.mlx_loop_exit(ptr)
            return
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if rlist:
            ch = sys.stdin.read(1)
            if ch == "\x03":
                m.mlx_loop_exit(ptr)

    m.mlx_loop_hook(ptr, on_loop, None)

    fd, old_attrs = disable_term_signals(
        vmin=0, vtime=0,
    )
    try:
        m.mlx_loop(ptr)
    except SystemExit:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_attrs)


# ---- Frame building --------------------------------------

def _build_frame(
    mlx_env: Tuple[Any, Any, Any],
    ctx: MazeContext, dims: _Dims, st: _MlxState,
) -> Any:
    """Build full-window image: maze + text."""
    m, ptr, win = mlx_env
    ni = m.mlx_new_image(ptr, dims.win_w, dims.win_h)
    r = m.mlx_get_data_addr(ni)
    buf = ImageBuffer(r[0], r[2], r[1] // 8)
    _fill(buf, pos=(0, 0),
          size=(dims.win_w, dims.win_h), col=BG)
    _draw_cells(buf, ctx, st)
    _draw_text(buf, dims, ctx.maze, st)
    m.mlx_put_image_to_window(ptr, win, ni, 0, 0)
    m.mlx_do_sync(ptr)
    return ni


def _draw_cells(
    buf: ImageBuffer, ctx: MazeContext, st: _MlxState,
) -> None:
    """Render all maze cells into image buffer."""
    maze = ctx.maze
    entry, exit_pos = ctx.entry, ctx.exit_pos
    wc = COLOURS[st.colours[0] % len(COLOURS)][1]
    pat_c = PAT_COLOURS[st.colours[1] % len(PAT_COLOURS)][1]
    pc = (
        _path_set(entry, st.path)
        if st.show_path and st.path else set()
    )
    ov = _CellOverlay(
        entry, exit_pos,
        set(maze.pattern_cells), pat_c,
        pc, st.explored,
    )
    for cy in range(maze.height):
        for cx in range(maze.width):
            px, py = PAD + cx * CELL, PAD + cy * CELL
            _draw_one_cell(buf, (cx, cy), (px, py), ov)
            _draw_walls(buf, px, py, maze.grid[cy][cx], wc)


def _draw_one_cell(
    buf: ImageBuffer,
    cell: Tuple[int, int],
    pixel: Tuple[int, int],
    ov: _CellOverlay,
) -> None:
    """Draw the interior of one cell."""
    px, py = pixel
    if cell == ov.entry:
        _fill(buf, pos=(px+2, py+2),
              size=(CELL-4, CELL-4), col=COL_ENTRY)
    elif cell == ov.exit_pos:
        _fill(buf, pos=(px+2, py+2),
              size=(CELL-4, CELL-4), col=COL_EXIT)
    elif cell in ov.pat:
        _fill(buf, pos=(px+1, py+1),
              size=(CELL-2, CELL-2), col=ov.pat_c)
    elif cell in ov.pc:
        ds = CELL // 3
        do = (CELL - ds) // 2
        _fill(buf, pos=(px+do, py+do),
              size=(ds, ds), col=COL_PATH)
    elif cell in ov.explored:
        ds = CELL // 3
        do = (CELL - ds) // 2
        _fill(buf, pos=(px+do, py+do),
              size=(ds, ds), col=COL_EXPLORED)


def _draw_walls(
    buf: ImageBuffer,
    px: int, py: int,
    cl: int, wc: int,
) -> None:
    """Draw walls for a single cell."""
    wl = CELL + WALL
    if cl & NORTH:
        _fill(buf, pos=(px, py), size=(wl, WALL), col=wc)
    if cl & SOUTH:
        _fill(buf, pos=(px, py+CELL),
              size=(wl, WALL), col=wc)
    if cl & WEST:
        _fill(buf, pos=(px, py), size=(WALL, wl), col=wc)
    if cl & EAST:
        _fill(buf, pos=(px+CELL, py),
              size=(WALL, wl), col=wc)


def _draw_text(
    buf: ImageBuffer, dims: _Dims,
    maze: Any, st: _MlxState,
) -> None:
    """Draw status text below the maze."""
    cn = COLOURS[st.colours[0] % len(COLOURS)][0]
    pn = PAT_COLOURS[st.colours[1] % len(PAT_COLOURS)][0]
    pf = "yes" if maze.perfect else "no"
    ty = PAD + dims.mh + PAD
    w = dims.win_w
    _put_text(buf, pos=(PAD, ty),
              text=f"Seed:{st.seed}  Algo:{maze.algorithm}",
              col=COL_TEXT, lim=w)
    _put_text(buf, pos=(PAD, ty + _CH),
              text=f"Solver:{st.solver}  Perfect:{pf}",
              col=COL_TEXT, lim=w)
    _put_text(buf, pos=(PAD, ty + 2*_CH),
              text=f"Walls:{cn}  42:{pn}  "
              f"Path:{'on' if st.show_path else 'off'}",
              col=COL_TEXT, lim=w)
    _put_text(buf, pos=(PAD, ty + 3*_CH),
              text="R:Regen P:Path C:Col S:Seed G:Algo",
              col=COL_HELP, lim=w)
    _put_text(buf, pos=(PAD, ty + 4*_CH),
              text="F:Solver X:Perf T:42 A:Anim V:Sol",
              col=COL_HELP, lim=w)
    if st.seed_input.active:
        _put_text(buf, pos=(PAD, ty - _CH - 4),
                  text=f"Seed> {st.seed_input.buf}_",
                  col=0xFFFF00, lim=w)


# ---- Key handling ----------------------------------------

def _handle_mlx_key(
    kc: int, ctx: MazeContext, st: _MlxState,
    cbs: Tuple[Any, Any, Any],
) -> None:
    """Handle a key event."""
    _, redraw, rebuild = cbs
    if st.seed_input.active:
        _handle_seed_mode(kc, ctx.maze, st, redraw, rebuild)
        return
    _handle_normal_key(kc, ctx, st, cbs)


def _handle_normal_key(
    kc: int, ctx: MazeContext, st: _MlxState,
    cbs: Tuple[Any, Any, Any],
) -> None:
    """Handle keys in normal (non-seed) mode."""
    mlx_exit, redraw, rebuild = cbs
    maze = ctx.maze
    entry, exit_pos = ctx.entry, ctx.exit_pos
    if kc in (65307, 113):
        mlx_exit()
    elif kc == 114:  # r
        _mlx_regen(maze, st, rebuild)
    elif kc == 112:  # p
        st.show_path = not st.show_path
        redraw()
    elif kc == 99:  # c
        st.colours[0] = (st.colours[0] + 1) % len(COLOURS)
        redraw()
    elif kc == 116:  # t
        st.colours[1] = (st.colours[1] + 1) % len(PAT_COLOURS)
        redraw()
    elif kc == 115:  # s
        st.seed_input.active = True
        st.seed_input.buf = ""
        redraw()
    elif kc == 103:  # g
        ai = _ALGORITHMS.index(maze.algorithm)
        maze.algorithm = _ALGORITHMS[
            (ai + 1) % len(_ALGORITHMS)
        ]
        rebuild()
    elif kc == 102:  # f
        si = _SOLVERS.index(st.solver)
        st.solver = _SOLVERS[(si + 1) % len(_SOLVERS)]
        try:
            st.path = maze.solve(
                entry, exit_pos, solver=st.solver,
            )
        except ValueError:
            st.path = ""
        redraw()
    elif kc == 120:  # x
        maze.perfect = not maze.perfect
        rebuild()
    elif kc == 97:  # a
        _mlx_anim_gen(ctx, st, redraw, rebuild)
    elif kc == 118:  # v
        _mlx_anim_sol(ctx, st, redraw)


def _mlx_regen(
    maze: Any, st: _MlxState, rebuild: Any,
) -> None:
    """Regenerate with incremented seed."""
    if st.seed is not None:
        st.seed = st.seed + 1
    else:
        st.seed = int(time.time())
    maze.seed = st.seed
    rebuild()


def _handle_seed_mode(
    kc: int, maze: Any, st: _MlxState,
    redraw: Any, rebuild: Any,
) -> None:
    """Handle keys while in seed-entry mode."""
    if kc == 65307:
        st.seed_input.active = False
        st.seed_input.buf = ""
        redraw()
    elif kc == 65293:
        try:
            st.seed = int(st.seed_input.buf)
        except ValueError:
            st.seed_input.active = False
            st.seed_input.buf = ""
            redraw()
            return
        st.seed_input.active = False
        st.seed_input.buf = ""
        maze.seed = st.seed
        rebuild()
    elif kc == 65288:
        st.seed_input.buf = st.seed_input.buf[:-1]
        redraw()
    elif 48 <= kc <= 57:
        st.seed_input.buf += chr(kc)
        redraw()
    elif kc == 45 and not st.seed_input.buf:
        st.seed_input.buf = "-"
        redraw()


# ---- Animations -----------------------------------------

def _mlx_anim_gen(
    ctx: MazeContext, st: _MlxState,
    redraw: Any, rebuild: Any,
) -> None:
    """Animate generation in MLX display."""
    maze = ctx.maze
    maze.seed = st.seed
    rng = create_rng(st.seed)
    maze.pattern_cells.clear()
    st.path = ""
    maze.grid = [
        [ALL_WALLS] * maze.width
        for _ in range(maze.height)
    ]
    iv = max(1, (maze.width * maze.height) // 60)

    def on_step(step: int) -> None:
        if not step % iv:
            redraw()
            time.sleep(0.02)

    animate_gen_steps(
        maze, rng, on_step,
        should_stop=lambda: st.quit_flag,
    )
    if st.quit_flag:
        rebuild()
        return
    st.path = finalize_generation(ctx, st.solver)
    redraw()


def _mlx_anim_sol(
    ctx: MazeContext, st: _MlxState, redraw: Any,
) -> None:
    """Animate solving in MLX display."""
    maze = ctx.maze
    iv = max(1, (maze.width * maze.height) // 40)
    st.show_path = False
    st.path = ""
    st.explored = {ctx.entry}

    def on_step(
        step: int, explored: Set[Tuple[int, int]],
    ) -> None:
        st.explored = explored
        if not step % iv:
            redraw()
            time.sleep(0.02)

    result = animate_solve_steps(
        maze, (ctx.entry, ctx.exit_pos),
        st.solver, on_step=on_step,
        should_stop=lambda: st.quit_flag,
    )
    if st.quit_flag:
        st.show_path = True
        st.explored = set()
        redraw()
        return
    st.path = result or ""
    st.show_path = True
    st.explored = set()
    redraw()
