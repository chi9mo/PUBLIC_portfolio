"""Output file writer for maze data.

Writes the maze grid in hexadecimal format along with entry/exit
coordinates and the shortest path.
"""

from typing import List, Tuple


def write_output(
    filepath: str,
    grid: List[List[int]],
    entry: Tuple[int, int],
    exit_pos: Tuple[int, int],
    path: str,
) -> None:
    """Write maze data to an output file.

    Format:
        - Hex grid rows (one hex digit per cell, one row per line)
        - Empty line
        - Entry coordinates (x,y)
        - Exit coordinates (x,y)
        - Shortest path (N/E/S/W characters)

    All lines end with newline.

    Args:
        filepath: Path to the output file.
        grid: 2D list of wall-encoded cell values (0-15).
        entry: (x, y) entry coordinates.
        exit_pos: (x, y) exit coordinates.
        path: Shortest path string (N/E/S/W).

    Raises:
        IOError: If file cannot be written.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        for row in grid:
            line: str = "".join(
                format(cell, "X") for cell in row
            )
            f.write(line + "\n")
        f.write("\n")
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit_pos[0]},{exit_pos[1]}\n")
        f.write(path + "\n")
