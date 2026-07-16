"""
Data models for converter.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Elements:
    headers: int = 0
    lists: int = 0
    code_blocks: int = 0
    links: int = 0
    tables: int = 0
    tasks: int = 0
    quotes: int = 0


@dataclass
class ConversionStats:
    original_chars: int
    markdown_chars: int
    tokens_saved: int
    compression_ratio: float
    time_ms: float
    elements: Elements = field(default_factory=Elements)


@dataclass
class ConversionResult:
    markdown: str
    stats: ConversionStats
    warnings: List[str] = field(default_factory=list)