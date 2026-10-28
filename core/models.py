"""Structures de données partagées entre les modules."""
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path


class InstallStatus(Enum):
    INSTALLED = auto()
    SKIPPED_DUPLICATE = auto()
    FAILED = auto()


@dataclass
class InstallResult:
    path: Path
    status: InstallStatus
    message: str
