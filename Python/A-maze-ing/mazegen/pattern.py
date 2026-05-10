"""Pattern placement for the '42' visual in mazes.

Defines pixel-art templates for digits '4' and '2', and places
them as fully-closed cells within the maze grid. After placement,
reconnects any disconnected non-pattern cells to restore maze
connectivity.
"""

from typing import List, Tuple, Optional, Set, Callable, TYPE_CHECKING
from collections import deque
import sys

from mazegen.generator import DIRECTION_DELTA, OPPOSITE

if TYPE_CHECKING:
    from mazegen.generator import MazeGenerator

# 5-row pixel art for digit '4' (3 columns wide)
DIGIT_4: List[List[int]] = [
    [1, 0, 0],
    [1, 0, 0],
    [1, 1, 1],
    [0, 0, 1],
    [0, 0, 1],
]

# 5-row pixel art for digit '2' (3 columns wide)
DIGIT_2: List[List[int]] = [
    [1, 1, 1],
    [0, 0, 1],
    [1, 1, 1],
    [1, 0, 0],
    [1, 1, 1],
]

# Gap between digits
DIGIT_GAP: int = 1

# Total pattern dimensions
PATTERN_WIDTH: int = 3 + DIGIT_GAP + 3  # 7
PATTERN_HEIGHT: int = 5

ALL_WALLS: int = 0xF


def get_pattern_cells() -> List[Tuple[int, int]]:
    """Get relative positions of filled cells in '42' pattern.

    Returns:
        List of (col, row) offsets where cells should be closed.
    """
    cells: List[Tuple[int, int]] = []
    for row in range(PATTERN_HEIGHT):
        for col in range(3):
            if DIGIT_4[row][col]:
                cells.append((col, row))
        for col in range(3):
            if DIGIT_2[row][col]:
                cells.append((col + 3 + DIGIT_GAP, row))
    return cells


def place_pattern(
    maze: "MazeGenerator",
    offset: Optional[Tuple[int, int]] = None,
) -> bool:
    """Place the '42' pattern and restore connectivity.

    Args:
        maze: The MazeGenerator instance to modify.
        offset: Optional (x, y) top-left position override.

    Returns:
        True if pattern was placed, False if maze is too small.
    """
    if not _check_size(maze):
        return False

    if offset is None:
        offset = (
            (maze.width - PATTERN_WIDTH) // 2,
            (maze.height - PATTERN_HEIGHT) // 2,
        )

    _close_pattern_cells(maze, offset)
    _reconnect(maze)
    return True


def _check_size(maze: "MazeGenerator") -> bool:
    """Return True if maze is large enough for the pattern."""
    if (
        maze.width < PATTERN_WIDTH + 2
        or maze.height < PATTERN_HEIGHT + 2
    ):
        print(
            "Warning: Maze too small for '42' pattern "
            f"(need at least {PATTERN_WIDTH + 2}x"
            f"{PATTERN_HEIGHT + 2}), skipping.",
            file=sys.stderr,
        )
        return False
    return True


def _close_pattern_cells(
    maze: "MazeGenerator",
    offset: Tuple[int, int],
) -> None:
    """Close all walls on pattern cells and their neighbours."""
    ox, oy = offset
    pattern = get_pattern_cells()
    for dx, dy in pattern:
        x, y = ox + dx, oy + dy
        maze.grid[y][x] = ALL_WALLS
        maze.pattern_cells.add((x, y))
        for wall, (ddx, ddy) in DIRECTION_DELTA.items():
            nx, ny = x + ddx, y + ddy
            if maze.in_bounds(nx, ny):
                maze.grid[ny][nx] |= OPPOSITE[wall]


def _flood_fill(
    maze: "MazeGenerator",
    start: Tuple[int, int],
    pattern_cells: Set[Tuple[int, int]],
) -> Set[Tuple[int, int]]:
    """BFS flood fill from start, skipping pattern cells.

    Args:
        maze: MazeGenerator instance.
        start: Starting cell (x, y).
        pattern_cells: Cells to skip.

    Returns:
        Set of reachable non-pattern cells.
    """
    visited: Set[Tuple[int, int]] = {start}
    queue: deque[Tuple[int, int]] = deque([start])

    while queue:
        x, y = queue.popleft()
        for wall, (dx, dy) in DIRECTION_DELTA.items():
            if maze.grid[y][x] & wall:
                continue
            nx, ny = x + dx, y + dy
            if (
                maze.in_bounds(nx, ny)
                and (nx, ny) not in visited
                and (nx, ny) not in pattern_cells
            ):
                visited.add((nx, ny))
                queue.append((nx, ny))

    return visited


def _reconnect(maze: "MazeGenerator") -> None:
    """Reconnect disconnected regions after pattern placement."""
    pcells: Set[Tuple[int, int]] = maze.pattern_cells
    all_non_pattern = _non_pattern_cells(maze, pcells)

    if not all_non_pattern:
        return

    components = _find_components(maze, all_non_pattern, pcells)
    if len(components) <= 1:
        return

    _merge_components(maze, components, pcells)


def _non_pattern_cells(
    maze: "MazeGenerator",
    pcells: Set[Tuple[int, int]],
) -> Set[Tuple[int, int]]:
    """Return all cells not in the pattern."""
    result: Set[Tuple[int, int]] = set()
    for y in range(maze.height):
        for x in range(maze.width):
            if (x, y) not in pcells:
                result.add((x, y))
    return result


def _find_components(
    maze: "MazeGenerator",
    all_cells: Set[Tuple[int, int]],
    pcells: Set[Tuple[int, int]],
) -> List[Set[Tuple[int, int]]]:
    """Find connected components among non-pattern cells."""
    components: List[Set[Tuple[int, int]]] = []
    remaining: Set[Tuple[int, int]] = set(all_cells)
    while remaining:
        start: Tuple[int, int] = next(iter(remaining))
        comp: Set[Tuple[int, int]] = _flood_fill(
            maze, start, pcells
        )
        components.append(comp)
        remaining -= comp
    return components


def _merge_components(
    maze: "MazeGenerator",
    components: List[Set[Tuple[int, int]]],
    pcells: Set[Tuple[int, int]],
) -> None:
    """Merge components by opening walls between adjacent cells."""
    comp_id: dict[Tuple[int, int], int] = {}
    for i, comp in enumerate(components):
        for cell in comp:
            comp_id[cell] = i

    parent: List[int] = list(range(len(components)))

    def find(n: int) -> int:
        """Find root of component set."""
        while parent[n] != n:
            parent[n] = parent[parent[n]]
            n = parent[n]
        return n

    uf = (parent, find)
    for y in range(maze.height):
        for x in range(maze.width):
            if (x, y) not in pcells:
                _try_merge_at(
                    maze, (x, y), pcells,
                    comp_id, uf,
                )


def _try_merge_at(
    maze: "MazeGenerator",
    cell: Tuple[int, int],
    pcells: Set[Tuple[int, int]],
    comp_id: dict[Tuple[int, int], int],
    uf: Tuple[List[int], Callable[[int], int]],
) -> None:
    """Open walls to merge different components at cell."""
    parent, find = uf
    for wall, (dx, dy) in DIRECTION_DELTA.items():
        nx, ny = cell[0] + dx, cell[1] + dy
        if not maze.in_bounds(nx, ny) or (nx, ny) in pcells:
            continue
        ci, cj = find(comp_id[cell]), find(comp_id[(nx, ny)])
        if ci != cj:
            maze.carve(cell[0], cell[1], wall)
            if find(ci) != find(cj):
                parent[find(cj)] = find(ci)
