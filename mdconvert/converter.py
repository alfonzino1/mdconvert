"""
Main converter engine with smart detection pipeline.
"""
from .patterns import PatternDetector, PatternMatch
from .formatters import get_formatter
from .stats import StatsCalculator
from .models import Elements, ConversionStats, ConversionResult
import re
import time
from typing import List

class MarkdownConverter:
    """Smart converter with pattern detection."""
    
    def __init__(self, format_style: str = 'claude'):
        self.detector = PatternDetector()
        self.formatter = get_formatter(format_style)
        self.stats_calc = StatsCalculator()
    
    def convert(self, text: str, smart: bool = True) -> ConversionResult:
        """Convert text to markdown."""
        start_time = time.perf_counter()
        
        if not text.strip():
            return ConversionResult(
                markdown="",
                stats=ConversionStats(0, 0, 0, 0.0, 0.0),
                warnings=["Empty input"]
            )
        
        lines = text.split('\n')
        result = []
        elements = Elements()
        context = {
            'line_number': 0,
            'prev_empty': False,
            'in_list': False,
            'in_code_block': False,
            'is_header': False,
            'prev_has_commas': False,
        }
        
        for i, line in enumerate(lines):
            context['line_number'] = i
            context['prev_empty'] = (i > 0 and not lines[i-1].strip())
            context['prev_has_commas'] = (i > 0 and ',' in lines[i-1])
            
            # Empty line handling
            if not line.strip():
                context['in_list'] = False
                result.append('')
                continue
            
            # Try pattern detection
            match = self.detector.detect(line, context)
            
            if match:
                result.append(match.markdown)
                self._update_elements(match, elements)
                
                # Update context
                if match.element_type in ('bullet_list', 'numbered_list', 'task_list'):
                    context['in_list'] = True
                elif match.element_type in ('h1', 'h2', 'h3', 'h4'):
                    context['is_header'] = True
                else:
                    context['is_header'] = False
            else:
                # Handle emphasis within lines
                processed = self._apply_inline_formatting(line)
                result.append(processed)
                context['in_list'] = False
                context['is_header'] = False
        
        # Join and format
        markdown = '\n'.join(result)
        markdown = self.formatter.format(markdown)
        
        # Calculate stats
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        stats = self.stats_calc.calculate(text, markdown, elements, elapsed_ms)
        
        # Generate warnings
        warnings = self._generate_warnings(elements, text)
        
        return ConversionResult(
            markdown=markdown.strip(),
            stats=stats,
            warnings=warnings,
        )
    
    def _apply_inline_formatting(self, line: str) -> str:
        """Apply inline formatting to text."""
        # Bold **text**
        line = re.sub(r'\*\*(.+?)\*\*', r'**\1**', line)
        
        # Italic *text*
        line = re.sub(r'(?<!\*)\*(.+?)\*(?!\*)', r'*\1*', line)
        
        # Inline code `code`
        line = re.sub(r'`(.+?)`', r'`\1`', line)
        
        # Strikethrough ~~text~~
        line = re.sub(r'~~(.+?)~~', r'~~\1~~', line)
        
        return line
    
    def _update_elements(self, match: PatternMatch, elements: Elements):
        """Update element counters based on match type."""
        if match.element_type.startswith('h'):
            elements.headers += 1
        elif 'list' in match.element_type:
            elements.lists += 1
        elif match.element_type == 'task_list':
            elements.tasks += 1
        elif 'code' in match.element_type:
            elements.code_blocks += 1
        elif match.element_type == 'link':
            elements.links += 1
        elif 'table' in match.element_type:
            elements.tables += 1
        elif match.element_type == 'blockquote':
            elements.quotes += 1
    
    def _generate_warnings(self, elements: Elements, text: str) -> List[str]:
        """Generate improvement suggestions."""
        warnings = []
        
        if elements.headers == 0 and len(text) > 200:
            warnings.append("No headers detected. Consider adding section titles with colons (:)")
        
        if elements.lists == 0 and text.count('\n') > 5:
            warnings.append("Long text without lists. Use '- ' for bullet points")
        
        if len(text) > 1000 and elements.headers < 2:
            warnings.append("Large text with few headers. Add sections for better readability")
        
        return warnings