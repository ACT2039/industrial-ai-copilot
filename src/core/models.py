"""
Enterprise Data Models
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict


@dataclass
class RawDocument:

    document_id: str

    path: Path

    file_name: str

    extension: str

    size_bytes: int = 0

    mime_type: str = ""

    readable: bool = False

    sha256: str = ""

    duplicate: bool = False

    metadata: Dict = field(default_factory=dict)