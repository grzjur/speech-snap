from pathlib import Path


class Paths:
    """Centralized file paths configuration."""

    def __init__(self, base_dir: str | None = None):
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent.parent
        else:
            self.base_dir = Path(base_dir)

    @property
    def path_to_data(self) -> Path:
        return self.base_dir / "data"