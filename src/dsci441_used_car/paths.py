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
    return Path(__file__).resolve().parents[3]


def get_paths() -> ProjectPaths:
    return ProjectPaths(repo_root=get_repo_root())

