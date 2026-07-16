"""
Statistics calculator for conversion results.
"""

from .models import Elements, ConversionStats


class StatsCalculator:
    """Calculates conversion statistics."""
    
    def calculate(self, original: str, markdown: str, 
                  elements: Elements, time_ms: float) -> ConversionStats:
        """Calculate all statistics."""
        original_chars = len(original)
        markdown_chars = len(markdown)
        tokens_saved = self._estimate_tokens_saved(original, markdown)
        compression = self._calculate_compression(original_chars, markdown_chars)
        
        return ConversionStats(
            original_chars=original_chars,
            markdown_chars=markdown_chars,
            tokens_saved=tokens_saved,
            compression_ratio=compression,
            time_ms=time_ms,
            elements=elements,
        )
    
    def _estimate_tokens_saved(self, original: str, markdown: str) -> int:
        """Estimate tokens saved (rough: 1 token ≈ 0.75 words)."""
        original_tokens = int(len(original.split()) / 0.75)
        markdown_tokens = int(len(markdown.split()) / 0.75)
        
        # Markdown syntax adds some tokens
        syntax_overhead = markdown.count('#') + markdown.count('*') + markdown.count('`')
        markdown_tokens += syntax_overhead
        
        saved = original_tokens - markdown_tokens
        return max(0, saved)
    
    def _calculate_compression(self, original_chars: int, markdown_chars: int) -> float:
        """Calculate compression ratio."""
        if original_chars == 0:
            return 0.0
        return 1 - (markdown_chars / original_chars)