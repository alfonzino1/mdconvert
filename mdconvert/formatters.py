"""
Output formatters for different platforms.
"""

import re
from typing import List


class BaseFormatter:
    """Base formatter with common utilities."""
    
    def format(self, text: str) -> str:
        return text
    
    def _normalize_spacing(self, text: str) -> str:
        """Remove excessive blank lines."""
        return re.sub(r'\n{3,}', '\n\n', text)
    
    def _add_section_spacing(self, text: str) -> str:
        """Ensure proper spacing around headers."""
        text = re.sub(r'(\n#{1,6}\s.*?\n)', r'\n\1', text)
        return text


class ClaudeFormatter(BaseFormatter):
    """Optimize for Claude's markdown parser."""
    
    def format(self, text: str) -> str:
        text = self._normalize_spacing(text)
        
        # Claude prefers:
        # - Concise headers
        # - Minimal blank lines
        # - Proper list spacing
        text = re.sub(r'\n{2,}', '\n\n', text)
        text = self._add_section_spacing(text)
        
        # Remove trailing spaces
        text = '\n'.join(line.rstrip() for line in text.split('\n'))
        
        return text


class GitHubFormatter(BaseFormatter):
    """Optimize for GitHub Flavored Markdown."""
    
    def format(self, text: str) -> str:
        text = self._normalize_spacing(text)
        
        # GitHub specifics:
        # - Auto-links are supported
        # - Task lists need proper spacing
        # - Tables need alignment row
        
        return text


class StandardFormatter(BaseFormatter):
    """Standard CommonMark."""
    
    def format(self, text: str) -> str:
        return self._normalize_spacing(text)


def get_formatter(name: str = 'claude') -> BaseFormatter:
    """Factory for formatters."""
    formatters = {
        'claude': ClaudeFormatter(),
        'github': GitHubFormatter(),
        'standard': StandardFormatter(),
    }
    return formatters.get(name, StandardFormatter())