"""A-Maze-ing — Maze generator and visualizer.

Main entry point for the maze generation program.
Reads a configuration file, generates a maze, writes output,
and launches a visual display.

Usage:
    python3 a_maze_ing.py config.txt
"""

import sys
from typing import Dict, Any, Tuple

from mazegen.config import parse_config
from mazegen.generator import MazeGenerator
from mazegen.pattern import place_pattern
from mazegen.output import write_output
from display import MazeContext
from display.ascii_display import interactive_ascii
from display.mlx_display import run_mlx_display, MLX_AVAILABLE


def main() -> None:
    """Run the maze generator pipeline.

    Parses command-line arguments, loads configuration,
    generates a maze, solves it, writes the output file,
    and launches the visual display.
    """
    if len(sys.argv) != 2:
        print(
            f"Usage: python3 {sys.argv[0]} <config_file>",
            file=sys.stderr,
        )
        sys.exit(1)

    config_path: str = sys.argv[1]

    try:
        config: Dict[str, Any] = parse_config(config_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        maze, path_str = _generate_and_solve(config)
    except (KeyboardInterrupt, SystemExit):
        print()
        sys.exit(130)
    except ValueError as e:
        print(f"Maze generation error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        _write_output(config, maze, path_str)
    except (KeyboardInterrupt, SystemExit):
        print()
        sys.exit(130)
    except IOError as e:
        print(f"Output error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        _launch_display(config, maze, path_str)
    except (KeyboardInterrupt, SystemExit):
        print()
        sys.exit(130)

    sys.exit(0)


def _generate_and_solve(
    config: Dict[str, Any],
) -> Tuple[MazeGenerator, str]:
    """Generate the maze and find the shortest path.

    Args:
        config: Parsed configuration dictionary.

    Returns:
        Tuple of (MazeGenerator instance, path string).

    Raises:
        ValueError: If maze cannot be generated or solved.
    """
    maze: MazeGenerator = MazeGenerator(
        width=config["width"],
        height=config["height"],
        seed=config["seed"],
        perfect=config["perfect"],
    )

    maze.generate(algorithm=config["algorithm"])
    place_pattern(maze)

    entry: Tuple[int, int] = config["entry"]
    exit_pos: Tuple[int, int] = config["exit"]

    if not maze.perfect:
        maze.remove_random_walls(
            entry=entry, exit_pos=exit_pos,
        )

    path_str: str = maze.solve(
        entry, exit_pos, solver=config["solver"]
    )

    print(
        f"Maze generated: {config['width']}x"
        f"{config['height']}, "
        f"algorithm={config['algorithm']}, "
        f"seed={config['seed']}, "
        f"perfect={config['perfect']}"
    )
    print(
        f"Path length: {len(path_str)} "
        f"(solver={config['solver']})"
    )

    return maze, path_str


def _write_output(
    config: Dict[str, Any],
    maze: MazeGenerator,
    path_str: str,
) -> None:
    """Write the maze output file.

    Args:
        config: Parsed configuration dictionary.
        maze: MazeGenerator with generated grid.
        path_str: Shortest path string.

    Raises:
        IOError: If file cannot be written.
    """
    write_output(
        filepath=config["output_file"],
        grid=maze.grid,
        entry=config["entry"],
        exit_pos=config["exit"],
        path=path_str,
    )
    print(f"Output written to: {config['output_file']}")


def _launch_display(
    config: Dict[str, Any],
    maze: MazeGenerator,
    path_str: str,
) -> None:
    """Launch the visual display.

    Respects the DISPLAY config key (ascii/mlx).
    Falls back to ASCII if MLX is unavailable or errors.

    Args:
        config: Parsed configuration dictionary.
        maze: MazeGenerator with generated grid.
        path_str: Shortest path string.
    """
    entry: Tuple[int, int] = config["entry"]
    exit_pos: Tuple[int, int] = config["exit"]
    display_mode: str = config.get("display", "mlx")
    ctx = MazeContext(maze, entry, exit_pos)

    if display_mode == "ascii":
        print("Using ASCII display (config).")
        interactive_ascii(
            ctx, path_str,
            config["seed"],
            config["solver"],
        )
        return

    if MLX_AVAILABLE:
        try:
            print("Launching MLX display...")
            run_mlx_display(
                ctx, path_str,
                config["seed"],
                config["solver"],
            )
            return
        except (OSError, RuntimeError) as exc:
            print(
                f"MLX display error: {exc}",
                file=sys.stderr,
            )
            print(
                "Falling back to ASCII.",
                file=sys.stderr,
            )
    else:
        print(
            "MLX not installed. "
            "Falling back to ASCII.",
            file=sys.stderr,
        )

    interactive_ascii(
        ctx, path_str,
        config["seed"],
        config["solver"],
    )


if __name__ == "__main__":
    main()
