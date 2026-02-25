from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    repo_root: Path

    @property
    def data_root(self) -> Path:
        return self.repo_root / "data" / "craigslist"

    @property
    def results_dir(self) -> Path:
        return self.repo_root / "results"

    @property
    def runs_dir(self) -> Path:
        return self.repo_root / "runs"


def get_repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        # Repo root marker (lightweight + robust even when installed editable).
        if (p / "pyproject.toml").exists() and (p / "src").exists():
            return p
    # Fallback to the typical src-layout structure.
    return here.parents[2]


def get_paths() -> ProjectPaths:
    return ProjectPaths(repo_root=get_repo_root())
