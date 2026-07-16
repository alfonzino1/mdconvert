"""
Pattern detection rules for smart text-to-markdown conversion.
Each pattern returns (is_match: bool, markdown: str, element_type: str)
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class PatternMatch:
    markdown: str
    element_type: str
    confidence: float  # 0.0 to 1.0


class PatternDetector:
    """Detects text patterns and converts to appropriate markdown."""
    
    def __init__(self):
        self.patterns = [
            self.detect_code_block,
            self.detect_table,
            self.detect_horizontal_rule,
            self.detect_task_list,
            self.detect_numbered_list,
            self.detect_bullet_list,
            self.detect_blockquote,
            self.detect_link,
            self.detect_header,
            self.detect_definition_list,
]
    
    def detect(self, line: str, context: dict) -> Optional[PatternMatch]:
        """Run all detectors and return best match."""
        for detector in self.patterns:
            result = detector(line, context)
            if result:
                return result
        return None
    
    def detect_header(self, line: str, context: dict) -> Optional[PatternMatch]:
        """Detect headers based on various heuristics."""
        stripped = line.strip()
        line_num = context.get('line_number', 0)
        prev_empty = context.get('prev_empty', False)
        
        # First non-empty line = H1
        if line_num == 0 and stripped and len(stripped) < 100:
            if not stripped.startswith('#'):
                return PatternMatch(
                    markdown=f"# {stripped}",
                    element_type='h1',
                    confidence=0.9
                )
        
        # Line ending with colon = H2
        if stripped.endswith(':') and len(stripped) < 80:
            if not stripped.startswith('#') and not stripped.startswith('-'):
                return PatternMatch(
                    markdown=f"## {stripped}",
                    element_type='h2',
                    confidence=0.85
                )
        
        # ALL CAPS short line = H3
        if (stripped.isupper() and len(stripped) < 60 
            and not any(c.isdigit() for c in stripped)):
            if not stripped.startswith('#'):
                return PatternMatch(
                    markdown=f"### {stripped}",
                    element_type='h3',
                    confidence=0.8
                )
        
        # Line with only numbers and dots (like "1.2.3") = H4
        if re.match(r'^[\d\.]+\s+[A-Z]', stripped):
            return PatternMatch(
                markdown=f"#### {stripped}",
                element_type='h4',
                confidence=0.7
            )
        
        return None
    
    def detect_numbered_list(self, line: str, context: dict) -> Optional[PatternMatch]:
        """Detect numbered lists."""
        stripped = line.strip()
        
        # Pattern: "1. Text" or "1) Text"
        match = re.match(r'^(\d+)[\.\)]\s*(.+)', stripped)
        if match:
            num, text = match.groups()
            return PatternMatch(
                markdown=f"{num}. {text.strip()}",
                element_type='numbered_list',
                confidence=0.95
            )
        
        return None
    
    def detect_bullet_list(self, line: str, context: dict) -> Optional[PatternMatch]:
        """Detect bullet lists."""
        stripped = line.strip()
        
        # Pattern: "- Text" or "* Text" or "+ Text"
        if re.match(r'^[\-\*\+]\s', stripped):
            text = stripped[1:].strip()
            return PatternMatch(
                markdown=f"- {text}",
                element_type='bullet_list',
                confidence=0.95
            )
        
        # Lines starting with lowercase letter followed by period
        # in a sequence might be list items
        if context.get('in_list') and re.match(r'^[a-z]\)\s', stripped):
            text = stripped[2:].strip()
            return PatternMatch(
                markdown=f"- {text}",
                element_type='bullet_list',
                confidence=0.6
            )
        
        return None
    
    def detect_task_list(self, line: str, context: dict) -> Optional[PatternMatch]:
        """Detect task/check lists."""
        stripped = line.strip()
        
        # Pattern: "[ ] Task" or "[x] Task" or "[X] Task"
        match = re.match(r'^\[([ xX])\]\s*(.+)', stripped)
        if match:
            checked = match.group(1).lower()
            text = match.group(2)
            checkbox = 'x' if checked == 'x' else ' '
            return PatternMatch(
                markdown=f"- [{checkbox}] {text}",
                element_type='task_list',
                confidence=0.95
            )
        
        return None
    
    def detect_blockquote(self, line: str, context: dict) -> Optional[PatternMatch]:
        """Detect blockquotes."""
        stripped = line.strip()
        
        # Already a blockquote
        if stripped.startswith('>'):
            return PatternMatch(
                markdown=stripped,
                element_type='blockquote',
                confidence=1.0
            )
        
        # Text in quotes
        if stripped.startswith('"') and stripped.endswith('"') and len(stripped) > 20:
            inner = stripped[1:-1]
            return PatternMatch(
                markdown=f"> {inner}",
                element_type='blockquote',
                confidence=0.7
            )
        
        return None
    
    def detect_code_block(self, line: str, context: dict) -> Optional[PatternMatch]:
        """Detect code blocks."""
        stripped = line.strip()
        
        # Triple backtick fence
        if stripped.startswith('```'):
            return PatternMatch(
                markdown=stripped,
                element_type='code_fence',
                confidence=1.0
            )
        
        # Indented with 4+ spaces (likely code)
        if line.startswith('    ') and len(stripped) > 3:
            return PatternMatch(
                markdown=line,
                element_type='code_block',
                confidence=0.8
            )
        
        return None
    
    def detect_table(self, line: str, context: dict) -> Optional[PatternMatch]:
        """Detect tables."""
        stripped = line.strip()
        
        # Lines with multiple | separators
        if stripped.count('|') >= 2:
            return PatternMatch(
                markdown=stripped,
                element_type='table',
                confidence=0.9
            )
        
        # CSV-like lines in sequence
        if context.get('prev_has_commas') and stripped.count(',') >= 2:
            cells = [c.strip() for c in stripped.split(',')]
            return PatternMatch(
                markdown='| ' + ' | '.join(cells) + ' |',
                element_type='table_row',
                confidence=0.7
            )
        
        return None
    
    def detect_link(self, line: str, context: dict) -> Optional[PatternMatch]:
        """Detect URLs and convert to markdown links."""
        stripped = line.strip()
        
        # Plain URL
        url_match = re.match(r'^(https?://\S+)$', stripped)
        if url_match:
            url = url_match.group(1)
            return PatternMatch(
                markdown=f"<{url}>",
                element_type='link',
                confidence=0.9
            )
        
        # Text followed by URL: "Text http://..."
        link_match = re.match(r'^(.+)\s+(https?://\S+)$', stripped)
        if link_match:
            text, url = link_match.groups()
            return PatternMatch(
                markdown=f"[{text.strip()}]({url})",
                element_type='link',
                confidence=0.85
            )
        
        return None
    
    def detect_horizontal_rule(self, line: str, context: dict) -> Optional[PatternMatch]:
        """Detect horizontal rules."""
        stripped = line.strip()
        
        # Three or more dashes/asterisks/underscores
        if re.match(r'^[\-\*_]{3,}$', stripped):
            return PatternMatch(
                markdown='---',
                element_type='hr',
                confidence=1.0
            )
        
        # Common divider patterns
        if stripped in ['***', '---', '___', '* * *', '- - -']:
            return PatternMatch(
                markdown='---',
                element_type='hr',
                confidence=1.0
            )
        
        return None
    
    def detect_definition_list(self, line: str, context: dict) -> Optional[PatternMatch]:
        """Detect definition lists (term: definition)."""
        stripped = line.strip()
        
        # Pattern: "Term: definition" (short term, longer definition)
        match = re.match(r'^([\w\s]{2,40}):\s+(.{10,})$', stripped)
        if match and not context.get('is_header'):
            term, definition = match.groups()
            return PatternMatch(
                markdown=f"**{term.strip()}**: {definition.strip()}",
                element_type='definition',
                confidence=0.75
            )
        
        return None