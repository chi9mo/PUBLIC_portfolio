"""Configuration file parser for A-Maze-ing.

Parses KEY=VALUE config files, validates mandatory keys, and
returns a typed configuration dictionary.
"""

from typing import Dict, Tuple, Any


# Mandatory keys that must appear in every config file
MANDATORY_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT",
                  "OUTPUT_FILE", "PERFECT"}


def parse_config(filepath: str) -> Dict[str, Any]:
    """Parse a maze configuration file.

    Args:
        filepath: Path to the configuration file.

    Returns:
        Dictionary with validated configuration values.

    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config is malformed or invalid.
    """
    raw: Dict[str, str] = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ValueError(
                        f"Line {line_num}: invalid format "
                        f"(expected KEY=VALUE): {line!r}"
                    )
                key, _, value = line.partition("=")
                key = key.strip().upper()
                value = value.strip()
                if not key or not value:
                    raise ValueError(
                        f"Line {line_num}: empty key or value"
                    )
                raw[key] = value
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Configuration file not found: {filepath}"
        ) from exc

    missing = MANDATORY_KEYS - raw.keys()
    if missing:
        raise ValueError(
            f"Missing mandatory config keys: "
            f"{', '.join(sorted(missing))}"
        )

    config: Dict[str, Any] = {}
    config["width"] = _parse_positive_int(raw, "WIDTH")
    config["height"] = _parse_positive_int(raw, "HEIGHT")
    config["entry"] = _parse_coords(raw, "ENTRY")
    config["exit"] = _parse_coords(raw, "EXIT")
    config["output_file"] = raw["OUTPUT_FILE"]
    config["perfect"] = _parse_bool(raw, "PERFECT")
    config["seed"] = _parse_optional_int(raw, "SEED")
    config["algorithm"] = raw.get(
        "ALGORITHM", "recursive_backtracker"
    ).lower()
    config["display"] = raw.get(
        "DISPLAY", "mlx"
    ).lower()
    config["solver"] = raw.get(
        "SOLVER", "bfs"
    ).lower()

    _validate_config(config)
    return config


def _parse_positive_int(
    raw: Dict[str, str], key: str
) -> int:
    """Parse a positive integer value from config.

    Args:
        raw: Raw config key-value pairs.
        key: Key to look up.

    Returns:
        Parsed positive integer.

    Raises:
        ValueError: If value is not a positive integer.
    """
    try:
        val = int(raw[key])
    except ValueError as exc:
        raise ValueError(
            f"{key} must be a positive integer, "
            f"got: {raw[key]!r}"
        ) from exc
    if val <= 0:
        raise ValueError(
            f"{key} must be positive, got: {val}"
        )
    return val


def _parse_optional_int(
    raw: Dict[str, str], key: str
) -> int | None:
    """Parse an optional integer value from config.

    Args:
        raw: Raw config key-value pairs.
        key: Key to look up.

    Returns:
        Parsed integer or None if key is absent.

    Raises:
        ValueError: If value is present but not an integer.
    """
    if key not in raw:
        return None
    try:
        return int(raw[key])
    except ValueError as exc:
        raise ValueError(
            f"{key} must be an integer, got: {raw[key]!r}"
        ) from exc


def _parse_coords(
    raw: Dict[str, str], key: str
) -> Tuple[int, int]:
    """Parse coordinate pair (x,y) from config.

    Args:
        raw: Raw config key-value pairs.
        key: Key to look up.

    Returns:
        Tuple of (x, y) integers.

    Raises:
        ValueError: If value is not in x,y format.
    """
    val = raw[key]
    parts = val.split(",")
    if len(parts) != 2:
        raise ValueError(
            f"{key} must be in x,y format, got: {val!r}"
        )
    try:
        x = int(parts[0].strip())
        y = int(parts[1].strip())
    except ValueError as exc:
        raise ValueError(
            f"{key} coordinates must be integers, "
            f"got: {val!r}"
        ) from exc
    if x < 0 or y < 0:
        raise ValueError(
            f"{key} coordinates must be non-negative, "
            f"got: ({x}, {y})"
        )
    return (x, y)


def _parse_bool(raw: Dict[str, str], key: str) -> bool:
    """Parse a boolean value from config.

    Args:
        raw: Raw config key-value pairs.
        key: Key to look up.

    Returns:
        Boolean value.

    Raises:
        ValueError: If value is not a valid boolean string.
    """
    val = raw[key].lower()
    if val in ("true", "1", "yes"):
        return True
    if val in ("false", "0", "no"):
        return False
    raise ValueError(
        f"{key} must be True or False, got: {raw[key]!r}"
    )


def _validate_config(config: Dict[str, Any]) -> None:
    """Validate parsed configuration for logical consistency.

    Args:
        config: Parsed configuration dictionary.

    Raises:
        ValueError: If configuration is logically invalid.
    """
    w: int = config["width"]
    h: int = config["height"]
    entry: Tuple[int, int] = config["entry"]
    exit_pos: Tuple[int, int] = config["exit"]

    if entry == exit_pos:
        raise ValueError(
            "ENTRY and EXIT must be different positions"
        )

    if entry[0] >= w or entry[1] >= h:
        raise ValueError(
            f"ENTRY {entry} is outside maze bounds "
            f"({w}x{h})"
        )

    if exit_pos[0] >= w or exit_pos[1] >= h:
        raise ValueError(
            f"EXIT {exit_pos} is outside maze bounds "
            f"({w}x{h})"
        )

    valid_algos = {
        "recursive_backtracker", "kruskal", "prim"
    }
    algo: str = config["algorithm"]
    if algo not in valid_algos:
        raise ValueError(
            f"Unknown algorithm: {algo!r}. "
            f"Valid options: {', '.join(sorted(valid_algos))}"
        )

    valid_displays = {"ascii", "mlx"}
    display: str = config["display"]
    if display not in valid_displays:
        raise ValueError(
            f"Unknown display mode: {display!r}. "
            f"Valid options: "
            f"{', '.join(sorted(valid_displays))}"
        )

    valid_solvers = {"bfs", "bibfs", "astar"}
    solver: str = config["solver"]
    if solver not in valid_solvers:
        raise ValueError(
            f"Unknown solver: {solver!r}. "
            f"Valid options: "
            f"{', '.join(sorted(valid_solvers))}"
        )
