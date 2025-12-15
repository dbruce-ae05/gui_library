from pathlib import Path


def find(
    name: str,
    return_path_not_found: Path,
    return_parent: bool = True,
) -> Path:
    current: Path = Path(__file__).parent

    while current != current.parent:
        if current.joinpath(name).exists():
            if return_parent:
                return current
            return current.joinpath(name)

        current = current.parent

    return return_path_not_found
