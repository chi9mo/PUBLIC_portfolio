"""Maze generation and solving utilities.

This module provides a grid-based maze generator with multiple algorithms,
optional wall removal for imperfect mazes, and path solvers.
"""
from typing import Optional, List, Tuple, Dict, Set, Deque
from random import Random as _Random
from collections import deque
import heapq

MazeRng = _Random


def create_rng(seed: Optional[int]) -> MazeRng:
    """Return a random number generator configured with seed."""
    return MazeRng(seed)


CameFrom = Dict[
    Tuple[int, int],  # current cell
    Optional[Tuple[Tuple[int, int], int]]  # (previous cell), direction
]

NORTH = 0x1
EAST = 0x2
SOUTH = 0x4
WEST = 0x8

ALL_WALLS = 0xF

DIRECTION_DELTA = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0)
}

OPPOSITE = {
    NORTH: SOUTH,
    EAST: WEST,
    SOUTH: NORTH,
    WEST: EAST
}

DIRECTION_LETTER = {
    NORTH: 'N',
    EAST: 'E',
    SOUTH: 'S',
    WEST: 'W'
}


def _collect_edges(
        width: int, height: int
        ) -> List[Tuple[int, int, int]]:
    """Collect right and bottom cell edges for all positions in the grid."""
    edges: List[Tuple[int, int, int]] = []

    for y in range(height):
        for x in range(width):
            if x + 1 < width:
                edges.append((x, y, EAST))
            if y + 1 < height:
                edges.append((x, y, SOUTH))
    return edges


def _manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """Return the Manhattan distance between two cells."""
    return abs(b[0] - a[0]) + abs(b[1] - a[1])


def _add_frontier(
        maze: "MazeGenerator",
        x: int, y: int,
        visited: Set[Tuple[int, int]],
        f_walls: List[Tuple[int, int, int]]
        ) -> None:
    """Add candidate walls around (x, y) that lead to unvisited cells."""
    for wall, (dx, dy) in DIRECTION_DELTA.items():
        nx, ny = x + dx, y + dy
        if maze.in_bounds(nx, ny) and (nx, ny) not in visited:
            f_walls.append((x, y, wall))


def _prim_try_carve(
        maze: "MazeGenerator",
        x: int, y: int,
        wall: int,
        visited: Set[Tuple[int, int]]
        ) -> Optional[Tuple[int, int]]:
    """Carve a Prim frontier wall and return the newly visited cell if any."""
    dx, dy = DIRECTION_DELTA[wall]
    nx, ny = x + dx, y + dy

    if not maze.in_bounds(nx, ny):
        return None
    if (nx, ny) in visited and (x, y) in visited:
        return None

    maze.carve(x, y, wall)

    if (nx, ny) not in visited:
        return (nx, ny)
    if (x, y) not in visited:
        return (x, y)
    return None


class MazeGenerator:
    """Generate and solve rectangular mazes using multiple algorithms."""

    def __init__(
        self,
        width: int,
        height: int,
        *,
        seed: Optional[int] = None,
        perfect: bool = True
    ) -> None:
        """Initialize a maze generator for the given dimensions.

        Raises:
            ValueError: If width or height is not positive.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers.")

        self.width: int = width
        self.height: int = height
        self.seed: Optional[int] = seed
        self.perfect: bool = perfect
        self.algorithm: str = "recursive_backtracker"
        self.grid: List[List[int]] = [
            [ALL_WALLS] * width for _ in range(height)
            ]
        self.pattern_cells: Set[Tuple[int, int]] = set()

    def generate(
            self,
            algorithm: Optional[str] = None
            ) -> None:
        """Generate a maze grid using the selected generation algorithm.

        Args:
            algorithm: One of recursive_backtracker, kruskal, or
                prim. If omitted,
                the previously selected algorithm is used.

        Raises:
            ValueError: If the algorithm name is unknown.
        """
        if algorithm is not None:
            self.algorithm = algorithm
        rng = create_rng(self.seed)

        self.grid = [
            [ALL_WALLS] * self.width for _ in range(self.height)
        ]

        if self.algorithm == "recursive_backtracker":
            self._generate_recursive_backtracker(rng)
        elif self.algorithm == "kruskal":
            self._generate_kruskal(rng)
        elif self.algorithm == "prim":
            self._generate_prim(rng)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm!r}")

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if (x, y) is inside the maze grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _set_wall(self, x: int, y: int, wall: int, build: bool) -> None:
        """Build or remove wall for a cell and its adjacent neighbor."""
        if build:
            self.grid[y][x] |= wall
        else:
            self.grid[y][x] &= ~wall

        opposite_wall = OPPOSITE[wall]
        dx, dy = DIRECTION_DELTA[wall]
        nx, ny = x + dx, y + dy

        if self.in_bounds(nx, ny):
            if build:
                self.grid[ny][nx] |= opposite_wall
            else:
                self.grid[ny][nx] &= ~opposite_wall

    def carve(self, x: int, y: int, wall: int) -> None:
        """Remove wall between a cell and its neighbor."""
        self._set_wall(x, y, wall, False)

    def _generate_recursive_backtracker(self, rng: MazeRng) -> None:
        """Generate a perfect maze using recursive backtracking."""
        visited: Set[Tuple[int, int]] = set()
        sx: int = rng.randint(0, self.width - 1)
        sy: int = rng.randint(0, self.height - 1)
        stack: List[Tuple[int, int]] = [(sx, sy)]
        visited.add((sx, sy))

        while stack:
            x, y = stack[-1]
            neighbors: List[Tuple[int, int, int]] = []
            for wall, (dx, dy) in DIRECTION_DELTA.items():
                nx, ny = x + dx, y + dy
                if (
                    self.in_bounds(nx, ny)
                    and (nx, ny) not in visited
                ):
                    neighbors.append((nx, ny, wall))

            if neighbors:
                rng.shuffle(neighbors)
                nx, ny, wall = neighbors[0]
                self.carve(x, y, wall)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

    def _generate_kruskal(self, rng: MazeRng) -> None:
        """Generate a perfect maze using Kruskal's algorithm."""
        parent: Dict[Tuple[int, int], Tuple[int, int]] = {}
        rank: Dict[Tuple[int, int], int] = {}

        for y in range(self.height):
            for x in range(self.width):
                parent[(x, y)] = (x, y)
                rank[(x, y)] = 0

        def find(n: Tuple[int, int]) -> Tuple[int, int]:
            while parent[n] != n:
                parent[n] = parent[parent[n]]
                n = parent[n]
            return n

        def union(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
            ra, rb = find(a), find(b)
            if ra == rb:
                return False
            if rank[ra] < rank[rb]:
                ra, rb = rb, ra
            parent[rb] = ra

            if rank[ra] == rank[rb]:
                rank[ra] += 1
            return True

        edges = _collect_edges(self.width, self.height)
        rng.shuffle(edges)

        for x, y, wall in edges:
            dx, dy = DIRECTION_DELTA[wall]
            nx, ny = x + dx, y + dy
            if union((x, y), (nx, ny)):
                self.carve(x, y, wall)

    def _generate_prim(self, rng: MazeRng) -> None:
        """Generate a perfect maze using randomized Prim's algorithm."""
        f_walls: List[Tuple[int, int, int]] = []

        sx = rng.randint(0, self.width - 1)
        sy = rng.randint(0, self.height - 1)
        visited: Set[Tuple[int, int]] = {(sx, sy)}

        _add_frontier(self, sx, sy, visited, f_walls)

        while f_walls:
            idx = rng.randint(0, len(f_walls) - 1)
            f_walls[idx], f_walls[-1] = f_walls[-1], f_walls[idx]

            x, y, wall = f_walls.pop()

            n_cell = _prim_try_carve(self, x, y, wall, visited)
            if n_cell is not None:
                visited.add(n_cell)
                _add_frontier(self, n_cell[0], n_cell[1], visited, f_walls)

    def _any_3x3_open(self) -> bool:
        """Return True if any fully open 3x3 region exists."""
        for y in range(self.height - 2):
            for x in range(self.width - 2):
                is_open = True
                for dy in range(3):
                    if not is_open:
                        break
                    for dx in range(3):
                        cx, cy = x + dx, y + dy
                        if dx < 2 and self._get_wall(cx, cy, EAST):
                            is_open = False
                            break
                        if dy < 2 and self._get_wall(cx, cy, SOUTH):
                            is_open = False
                            break
                if is_open:
                    return True
        return False

    def _collect_internal_walls(self) -> List[Tuple[int, int, int]]:
        """Collect removable internal walls outside pattern_cells."""
        walls: List[Tuple[int, int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue
                self.try_add_wall(walls, x, y, EAST)
                self.try_add_wall(walls, x, y, SOUTH)
        return walls

    def try_add_wall(
            self,
            walls: List[Tuple[int, int, int]],
            x: int, y: int,
            direction: int
    ) -> None:
        """Append a wall candidate if it is internal and currently present."""
        dx, dy = DIRECTION_DELTA[direction]
        nx, ny = x + dx, y + dy
        if (
            self.in_bounds(nx, ny)
            and self._get_wall(x, y, direction)
            and (nx, ny) not in self.pattern_cells
        ):
            walls.append((x, y, direction))

    def _get_wall(self, x: int, y: int, wall: int) -> bool:
        """Return True if wall exists on the given cell."""
        return bool(self.grid[y][x] & wall)

    def _validate_position(
            self,
            position: Tuple[int, int],
            name: str
    ) -> None:
        """Validate that a position is inside the maze bounds."""
        x, y = position
        if not self.in_bounds(x, y):
            raise ValueError(
                f"{name} must be within maze bounds, got: {position!r}"
            )

    def _has_multiple_paths(
            self,
            entry: Tuple[int, int],
            exit_pos: Tuple[int, int]
    ) -> bool:
        """Return whether at least two distinct entry-to-exit paths exist."""
        came_from: CameFrom = {entry: None}
        queue: Deque[Tuple[int, int]] = deque([entry])

        while queue:
            x, y = queue.popleft()
            if (x, y) == exit_pos:
                break
            for wall, (dx, dy) in DIRECTION_DELTA.items():
                nx, ny = x + dx, y + dy
                if self.grid[y][x] & wall or not self.in_bounds(nx, ny):
                    continue
                if (nx, ny) not in came_from:
                    came_from[(nx, ny)] = ((x, y), wall)
                    queue.append((nx, ny))

        if exit_pos not in came_from:
            return False

        path_edges: List[Tuple[int, int, int]] = []
        current = exit_pos
        while came_from[current]:
            prev, wall = came_from[current]
            path_edges.append((prev[0], prev[1], wall))
            current = prev

        for px, py, wall in path_edges:
            self._set_wall(px, py, wall, True)

            visited: Set[Tuple[int, int]] = {entry}
            q: Deque[Tuple[int, int]] = deque([entry])
            found = False
            while q:
                x, y = q.popleft()
                if (x, y) == exit_pos:
                    found = True
                    break
                for w, (dx, dy) in DIRECTION_DELTA.items():
                    nx, ny = x + dx, y + dy
                    if self.grid[y][x] & w or not self.in_bounds(nx, ny):
                        continue
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        q.append((nx, ny))

            self._set_wall(px, py, wall, False)

            if found:
                return True

        return False

    def remove_random_walls(
            self,
            entry: Tuple[int, int],
            exit_pos: Tuple[int, int],
    ) -> None:
        """Remove random internal walls while avoiding fully open 3x3 areas.

        The method targets roughly 15% of removable internal walls and then
        ensures the maze has multiple paths between entry and exit_pos.

        Raises:
            ValueError: If positions are invalid
            or no valid wall can be removed.
        """
        self._validate_position(entry, "entry")
        self._validate_position(exit_pos, "exit_pos")

        rng = create_rng(self.seed)
        internal_walls = self._collect_internal_walls()

        if not internal_walls:
            raise ValueError("No internal walls to remove.")

        rng.shuffle(internal_walls)
        target: int = max(1, len(internal_walls) * 15 // 100)
        removed: int = 0

        for x, y, wall in internal_walls:
            if removed >= target:
                break
            self.carve(x, y, wall)

            if self._any_3x3_open():
                self._set_wall(x, y, wall, True)
            else:
                removed += 1

        if removed == 0:
            raise ValueError(
                "Failed to remove any walls without creating 3x3 open areas."
                )

        if not self._has_multiple_paths(entry, exit_pos):
            remaining = self._collect_internal_walls()
            rng.shuffle(remaining)
            for x, y, wall in remaining:
                self.carve(x, y, wall)
                if self._any_3x3_open():
                    self._set_wall(x, y, wall, True)
                    continue
                if self._has_multiple_paths(entry, exit_pos):
                    break

    def solve(
            self,
            entry: Tuple[int, int],
            exit_pos: Tuple[int, int],
            solver: str = "bfs"
              ) -> str:
        """Solve the maze and return a direction string from entry to exit.

        Args:
            entry: Starting cell coordinates.
            exit_pos: Goal cell coordinates.
            solver: One of bfs, bibfs, or astar.

        Raises:
            ValueError: If a position is invalid or the solver is unknown.
        """
        self._validate_position(entry, "entry")
        self._validate_position(exit_pos, "exit_pos")

        if entry == exit_pos:
            return ""
        if solver == "bfs":
            return self._solve_bfs(entry, exit_pos)
        if solver == "bibfs":
            return self._solve_bibfs(entry, exit_pos)
        if solver == "astar":
            return self._solve_astar(entry, exit_pos)
        raise ValueError(f"Unknown solver: {solver!r}")

    def _solve_bfs(
            self,
            entry: Tuple[int, int],
            exit_pos: Tuple[int, int]
    ) -> str:
        """Solve the maze with breadth-first search."""
        came_from: CameFrom = {entry: None}
        queue: Deque[Tuple[int, int]] = deque([entry])

        while queue:
            x, y = queue.popleft()

            if (x, y) == exit_pos:
                return self.reconstruct_path(came_from, exit_pos)

            for wall, (dx, dy) in DIRECTION_DELTA.items():
                nx, ny = x + dx, y + dy
                if (
                    self.grid[y][x] & wall
                    or not self.in_bounds(nx, ny)
                ):
                    continue

                if (nx, ny) not in came_from:
                    came_from[(nx, ny)] = ((x, y), wall)
                    queue.append((nx, ny))

        raise ValueError("No path found from entry to exit.")

    def _solve_bibfs(
            self,
            entry: Tuple[int, int],
            exit_pos: Tuple[int, int]
    ) -> str:
        """Solve the maze with bidirectional breadth-first search."""
        cf_fwd: CameFrom = {entry: None}
        cf_bwd: CameFrom = {exit_pos: None}
        q_fwd: Deque[Tuple[int, int]] = deque([entry])
        q_bwd: Deque[Tuple[int, int]] = deque([exit_pos])

        while q_fwd and q_bwd:
            # foward
            x, y = q_fwd.popleft()

            if (x, y) in cf_bwd:
                return self.merge_bibfs(cf_fwd, cf_bwd, (x, y))

            for wall, (dx, dy) in DIRECTION_DELTA.items():
                nx, ny = x + dx, y + dy
                if (
                    self.grid[y][x] & wall
                    or not self.in_bounds(nx, ny)
                ):
                    continue

                if (nx, ny) not in cf_fwd:
                    cf_fwd[(nx, ny)] = ((x, y), wall)
                    q_fwd.append((nx, ny))

                    if (nx, ny) in cf_bwd:
                        return self.merge_bibfs(cf_fwd, cf_bwd, (nx, ny))

            # backward
            x, y = q_bwd.popleft()

            if (x, y) in cf_fwd:
                return self.merge_bibfs(cf_fwd, cf_bwd, (x, y))

            for wall, (dx, dy) in DIRECTION_DELTA.items():
                nx, ny = x + dx, y + dy
                if (
                    self.grid[y][x] & wall
                    or not self.in_bounds(nx, ny)
                ):
                    continue

                if (nx, ny) not in cf_bwd:
                    cf_bwd[(nx, ny)] = ((x, y), wall)
                    q_bwd.append((nx, ny))

                    if (nx, ny) in cf_fwd:
                        return self.merge_bibfs(cf_fwd, cf_bwd, (nx, ny))
        raise ValueError("No path found from entry to exit.")

    def merge_bibfs(
            self,
            cf_fwd: CameFrom,
            cf_bwd: CameFrom,
            meeting_point: Tuple[int, int]
    ) -> str:
        """Merge forward and backward BFS traces into one path string."""
        fwd_path: str = self.reconstruct_path(cf_fwd, meeting_point)

        bwd_path: List[str] = []
        current: Tuple[int, int] = meeting_point
        while cf_bwd[current]:
            prev, wall = cf_bwd[current]
            bwd_path.append(DIRECTION_LETTER[OPPOSITE[wall]])
            current = prev

        return fwd_path + "".join(bwd_path)

    def _solve_astar(
            self,
            entry: Tuple[int, int],
            exit_pos: Tuple[int, int]
    ) -> str:
        """Solve the maze with A* search using Manhattan distance."""
        came_from: CameFrom = {entry: None}
        g: Dict[Tuple[int, int], int] = {entry: 0}
        counter: int = 0

        # f = g + h
        # (f, counter, x, y)
        open_set: List[Tuple[int, int, int, int]] = [
            (g[entry] + _manhattan(entry, exit_pos),
             counter, entry[0], entry[1])
            ]

        while open_set:
            _, _, x, y = heapq.heappop(open_set)

            if (x, y) == exit_pos:
                return self.reconstruct_path(came_from, exit_pos)

            cg: int = g[(x, y)]
            for wall, (dx, dy) in DIRECTION_DELTA.items():
                nx, ny = x + dx, y + dy
                if (
                    self.grid[y][x] & wall
                    or not self.in_bounds(nx, ny)
                ):
                    continue

                if (
                    (nx, ny) not in g
                    or cg + 1 < g[(nx, ny)]
                ):
                    g[(nx, ny)] = cg + 1
                    came_from[(nx, ny)] = ((x, y), wall)
                    counter += 1
                    heapq.heappush(
                        open_set,
                        (g[(nx, ny)] + _manhattan((nx, ny), exit_pos),
                            counter, nx, ny)
                    )
        raise ValueError("No path found from entry to exit.")

    def reconstruct_path(
            self,
            came_from: CameFrom,
            end_pos: Tuple[int, int]
    ) -> str:
        """Reconstruct and return a direction string from came_from."""
        path: List[str] = []
        current: Tuple[int, int] = end_pos

        while came_from[current]:
            prev, wall = came_from[current]
            path.append(DIRECTION_LETTER[wall])
            current = prev
        path.reverse()
        return "".join(path)
