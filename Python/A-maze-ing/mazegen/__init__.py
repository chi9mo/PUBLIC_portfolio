"""mazegen — Reusable maze generation package.

Provides the MazeGenerator class for generating random mazes
with configurable size, seed, algorithm, and perfection mode.

Usage:
    from mazegen import MazeGenerator

    gen = MazeGenerator(width=20, height=15, seed=42, perfect=True)
    gen.generate(algorithm="recursive_backtracker")
    grid = gen.grid          # 2D list of hex-encoded wall values
    path = gen.solve(entry=(0, 0), exit_pos=(19, 14))  # 'NESW...'
"""

from mazegen.generator import MazeGenerator

__all__ = ["MazeGenerator"]
__version__ = "1.0.0"
