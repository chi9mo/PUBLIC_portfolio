"""Shared animation logic for maze generation and solving.

Provides algorithm stepping with a callback for frame updates,
used by both ASCII and MLX display modules.
"""

import heapq
from collections import deque
from typing import Tuple, Set, Optional, Callable

from mazegen.generator import (
    MazeGenerator, EAST, SOUTH,
    ALL_WALLS, DIRECTION_DELTA, CameFrom,
    MazeRng, create_rng,
)
from mazegen.pattern import place_pattern
from display import MazeContext


# -- Union-Find helpers used by Kruskal animation --------

class UnionFind:
    """Lightweight union-find for cell grids."""

    def __init__(self, width: int, height: int) -> None:
        """Initialize union-find structure for a cell grid."""
        self.parent: dict[
            Tuple[int, int], Tuple[int, int]
        ] = {}
        self.rnk: dict[Tuple[int, int], int] = {}
        for ky in range(height):
            for kx in range(width):
                self.parent[(kx, ky)] = (kx, ky)
                self.rnk[(kx, ky)] = 0

    def find(self, n: Tuple[int, int]) -> Tuple[int, int]:
        """Find with path compression."""
        while self.parent[n] != n:
            self.parent[n] = self.parent[self.parent[n]]
            n = self.parent[n]
        return n

    def union(
        self, a: Tuple[int, int], b: Tuple[int, int],
    ) -> bool:
        """Union by rank. Return True if merged."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rnk[ra] < self.rnk[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rnk[ra] == self.rnk[rb]:
            self.rnk[ra] += 1
        return True


# -- Generation animation --------------------------------

def animate_gen_steps(
    maze: MazeGenerator,
    rng: MazeRng,
    on_step: Callable[[int], None],
    should_stop: Callable[[], bool] = lambda: False,
) -> None:
    """Run one generation algorithm, calling *on_step* periodically.

    Args:
        maze: Maze with grid already reset to ALL_WALLS.
        rng: Seeded random instance.
        on_step: Called with current step count.
        should_stop: Return True to abort early.
    """
    step = 0
    if maze.algorithm == "kruskal":
        step = _anim_kruskal(
            maze, rng, on_step, should_stop,
        )
    elif maze.algorithm == "prim":
        step = _anim_prim(
            maze, rng, on_step, should_stop,
        )
    else:
        step = _anim_backtracker(
            maze, rng, on_step, should_stop,
        )
    # suppress unused-variable; step kept for future use
    _ = step


def _anim_kruskal(
    maze: MazeGenerator,
    rng: MazeRng,
    on_step: Callable[[int], None],
    should_stop: Callable[[], bool],
) -> int:
    uf = UnionFind(maze.width, maze.height)
    edges: list[Tuple[int, int, int]] = []
    for ey in range(maze.height):
        for ex in range(maze.width):
            if ex + 1 < maze.width:
                edges.append((ex, ey, EAST))
            if ey + 1 < maze.height:
                edges.append((ex, ey, SOUTH))
    rng.shuffle(edges)
    step = 0
    for ex, ey, ew in edges:
        if should_stop():
            break
        edx, edy = DIRECTION_DELTA[ew]
        enx, eny = ex + edx, ey + edy
        if uf.union((ex, ey), (enx, eny)):
            maze.carve(ex, ey, ew)
        step += 1
        on_step(step)
    return step


def _anim_prim(
    maze: MazeGenerator,
    rng: MazeRng,
    on_step: Callable[[int], None],
    should_stop: Callable[[], bool],
) -> int:
    in_maze: set[Tuple[int, int]] = set()
    walls: list[Tuple[int, int, int]] = []
    sx = rng.randint(0, maze.width - 1)
    sy = rng.randint(0, maze.height - 1)
    in_maze.add((sx, sy))
    _prim_add_frontier(maze, sx, sy, in_maze, walls)
    step = 0
    while walls and not should_stop():
        idx = rng.randint(0, len(walls) - 1)
        walls[idx], walls[-1] = walls[-1], walls[idx]
        px, py, pw = walls.pop()
        cell = _prim_try(maze, px, py, pw, in_maze)
        if cell is not None:
            _prim_add_frontier(
                maze, cell[0], cell[1], in_maze, walls,
            )
        step += 1
        on_step(step)
    return step


def _prim_add_frontier(
    maze: MazeGenerator,
    cx: int, cy: int,
    in_maze: set[Tuple[int, int]],
    walls: list[Tuple[int, int, int]],
) -> None:
    """Add frontier walls around a cell."""
    for w, (dx, dy) in DIRECTION_DELTA.items():
        nx, ny = cx + dx, cy + dy
        if maze.in_bounds(nx, ny) and (nx, ny) not in in_maze:
            walls.append((cx, cy, w))


def _prim_try(
    maze: MazeGenerator,
    px: int, py: int, pw: int,
    in_maze: set[Tuple[int, int]],
) -> Optional[Tuple[int, int]]:
    """Try carving a wall for Prim's. Return new cell or None."""
    pdx, pdy = DIRECTION_DELTA[pw]
    pnx, pny = px + pdx, py + pdy
    if not maze.in_bounds(pnx, pny):
        return None
    if (pnx, pny) in in_maze and (px, py) in in_maze:
        return None
    cell = (
        (pnx, pny) if (pnx, pny) not in in_maze
        else (px, py)
    )
    maze.carve(px, py, pw)
    in_maze.add(cell)
    return cell


def _anim_backtracker(
    maze: MazeGenerator,
    rng: MazeRng,
    on_step: Callable[[int], None],
    should_stop: Callable[[], bool],
) -> int:
    vis: set[Tuple[int, int]] = set()
    start = (
        rng.randint(0, maze.width - 1),
        rng.randint(0, maze.height - 1),
    )
    stk: list[Tuple[int, int]] = [start]
    vis.add(start)
    step = 0
    while stk and not should_stop():
        nb = _unvisited_neighbours(maze, stk[-1], vis)
        if nb:
            rng.shuffle(nb)
            nx, ny, w = nb[0]
            maze.carve(stk[-1][0], stk[-1][1], w)
            vis.add((nx, ny))
            stk.append((nx, ny))
        else:
            stk.pop()
        step += 1
        on_step(step)
    return step


def _unvisited_neighbours(
    maze: MazeGenerator,
    cell: Tuple[int, int],
    vis: set[Tuple[int, int]],
) -> list[Tuple[int, int, int]]:
    """Return unvisited neighbour cells."""
    x, y = cell
    result: list[Tuple[int, int, int]] = []
    for w, (dx, dy) in DIRECTION_DELTA.items():
        nx, ny = x + dx, y + dy
        if maze.in_bounds(nx, ny) and (nx, ny) not in vis:
            result.append((nx, ny, w))
    return result


# -- Solve animation --------------------------------------

def animate_solve_steps(
    maze: MazeGenerator,
    endpoints: Tuple[Tuple[int, int], Tuple[int, int]],
    solver: str, *,
    on_step: Callable[[int, Set[Tuple[int, int]]], None],
    should_stop: Callable[[], bool] = lambda: False,
) -> Optional[str]:
    """Run a solver with step callbacks.

    Args:
        maze: MazeGenerator instance.
        endpoints: (entry, exit_pos) tuple.
        solver: Algorithm name.
        on_step: Called with (step, explored).
        should_stop: Return True to abort.

    Returns the path string, or None on failure.
    """
    if solver == "bibfs":
        return _anim_bibfs(
            maze, endpoints, on_step, should_stop,
        )
    if solver == "astar":
        return _anim_astar(
            maze, endpoints, on_step, should_stop,
        )
    return _anim_bfs(
        maze, endpoints, on_step, should_stop,
    )


def _anim_bfs(
    maze: MazeGenerator,
    endpoints: Tuple[Tuple[int, int], Tuple[int, int]],
    on_step: Callable[[int, Set[Tuple[int, int]]], None],
    should_stop: Callable[[], bool],
) -> Optional[str]:
    came_from: CameFrom = {endpoints[0]: None}
    explored: Set[Tuple[int, int]] = {endpoints[0]}
    q: deque[Tuple[int, int]] = deque([endpoints[0]])
    step = 0
    while q and not should_stop():
        x, y = q.popleft()
        if (x, y) == endpoints[1]:
            return maze.reconstruct_path(
                came_from, endpoints[1],
            )
        for wall, (dx, dy) in DIRECTION_DELTA.items():
            if maze.grid[y][x] & wall:
                continue
            nx, ny = x + dx, y + dy
            if maze.in_bounds(nx, ny) and (nx, ny) not in came_from:
                came_from[(nx, ny)] = ((x, y), wall)
                q.append((nx, ny))
                explored.add((nx, ny))
        step += 1
        on_step(step, explored)
    return None


def _anim_bibfs(
    maze: MazeGenerator,
    endpoints: Tuple[Tuple[int, int], Tuple[int, int]],
    on_step: Callable[[int, Set[Tuple[int, int]]], None],
    should_stop: Callable[[], bool],
) -> Optional[str]:
    entry, exit_pos = endpoints
    cf_fwd: CameFrom = {entry: None}
    cf_bwd: CameFrom = {exit_pos: None}
    q_fwd: deque[Tuple[int, int]] = deque([entry])
    q_bwd: deque[Tuple[int, int]] = deque([exit_pos])
    explored: Set[Tuple[int, int]] = {entry, exit_pos}
    meet: Optional[Tuple[int, int]] = None
    step = 0
    while q_fwd and q_bwd and not meet and not should_stop():
        meet = _bibfs_expand_fwd(
            maze, q_fwd, cf_fwd, cf_bwd, explored,
        )
        step += 1
        on_step(step, explored)
        if meet:
            break
        if not q_bwd:
            break
        meet = _bibfs_expand_bwd(
            maze, q_bwd, cf_fwd, cf_bwd, explored,
        )
        step += 1
        on_step(step, explored)
    if meet is None:
        return None
    return maze.merge_bibfs(cf_fwd, cf_bwd, meet)


def _bibfs_expand_fwd(
    maze: MazeGenerator,
    q_fwd: deque[Tuple[int, int]],
    cf_fwd: CameFrom,
    cf_bwd: CameFrom,
    explored: Set[Tuple[int, int]],
) -> Optional[Tuple[int, int]]:
    """Expand one node from forward queue."""
    x, y = q_fwd.popleft()
    if (x, y) in cf_bwd:
        return (x, y)
    for wall, (dx, dy) in DIRECTION_DELTA.items():
        if maze.grid[y][x] & wall:
            continue
        nx, ny = x + dx, y + dy
        if maze.in_bounds(nx, ny) and (nx, ny) not in cf_fwd:
            cf_fwd[(nx, ny)] = ((x, y), wall)
            q_fwd.append((nx, ny))
            explored.add((nx, ny))
            if (nx, ny) in cf_bwd:
                return (nx, ny)
    return None


def _bibfs_expand_bwd(
    maze: MazeGenerator,
    q_bwd: deque[Tuple[int, int]],
    cf_fwd: CameFrom,
    cf_bwd: CameFrom,
    explored: Set[Tuple[int, int]],
) -> Optional[Tuple[int, int]]:
    """Expand one node from backward queue."""
    x, y = q_bwd.popleft()
    if (x, y) in cf_fwd:
        return (x, y)
    for wall, (dx, dy) in DIRECTION_DELTA.items():
        if maze.grid[y][x] & wall:
            continue
        nx, ny = x + dx, y + dy
        if maze.in_bounds(nx, ny) and (nx, ny) not in cf_bwd:
            cf_bwd[(nx, ny)] = ((x, y), wall)
            q_bwd.append((nx, ny))
            explored.add((nx, ny))
            if (nx, ny) in cf_fwd:
                return (nx, ny)
    return None


def _anim_astar(
    maze: MazeGenerator,
    endpoints: Tuple[Tuple[int, int], Tuple[int, int]],
    on_step: Callable[[int, Set[Tuple[int, int]]], None],
    should_stop: Callable[[], bool],
) -> Optional[str]:
    entry, exit_pos = endpoints
    came_from: CameFrom = {entry: None}
    g: dict[Tuple[int, int], int] = {entry: 0}
    explored: Set[Tuple[int, int]] = {entry}
    cnt = [0]
    pq: list[Tuple[int, int, int, int]] = [
        (_manhattan(entry, exit_pos), 0, entry[0], entry[1])
    ]
    astar_state = (g, came_from, explored, cnt, pq)
    step = 0
    while pq and not should_stop():
        _, _, x, y = heapq.heappop(pq)
        if (x, y) == exit_pos:
            return maze.reconstruct_path(came_from, exit_pos)
        _astar_expand(maze, (x, y), exit_pos, astar_state)
        step += 1
        on_step(step, explored)
    return None


def _manhattan(
    a: Tuple[int, int], b: Tuple[int, int],
) -> int:
    """Manhattan distance heuristic."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


AStarState = Tuple[
    dict[Tuple[int, int], int],
    CameFrom,
    Set[Tuple[int, int]],
    list[int],
    list[Tuple[int, int, int, int]],
]


def _astar_expand(
    maze: MazeGenerator,
    cur: Tuple[int, int],
    exit_pos: Tuple[int, int],
    state: AStarState,
) -> None:
    """Expand one node in A* search."""
    g, came_from, explored, cnt, pq = state
    cg = g[cur]
    for wall, (dx, dy) in DIRECTION_DELTA.items():
        if maze.grid[cur[1]][cur[0]] & wall:
            continue
        nx, ny = cur[0] + dx, cur[1] + dy
        if not maze.in_bounds(nx, ny):
            continue
        if (nx, ny) not in g or cg + 1 < g[(nx, ny)]:
            g[(nx, ny)] = cg + 1
            came_from[(nx, ny)] = (cur, wall)
            explored.add((nx, ny))
            cnt[0] += 1
            heapq.heappush(
                pq,
                (cg + 1 + _manhattan((nx, ny), exit_pos),
                 cnt[0], nx, ny),
            )


# -- Full generation with finalize ------------------------

def full_animate_gen(
    ctx: MazeContext,
    on_step: Callable[[int], None],
    solver: str = "bfs",
    should_stop: Callable[[], bool] = lambda: False,
) -> str:
    """Reset grid, animate generation, place pattern, solve."""
    maze = ctx.maze
    rng = create_rng(maze.seed)
    maze.grid = [
        [ALL_WALLS] * maze.width
        for _ in range(maze.height)
    ]
    animate_gen_steps(maze, rng, on_step, should_stop)
    if should_stop():
        maze.generate()
    return finalize_generation(ctx, solver)


def finalize_generation(
    ctx: MazeContext, solver: str,
) -> str:
    """Place pattern and solve after generation."""
    maze = ctx.maze
    maze.pattern_cells.clear()
    place_pattern(maze)
    if not maze.perfect:
        try:
            maze.remove_random_walls(
                entry=ctx.entry, exit_pos=ctx.exit_pos,
            )
        except ValueError:
            maze.perfect = True
    try:
        return maze.solve(
            ctx.entry, ctx.exit_pos, solver=solver,
        )
    except ValueError:
        return ""
