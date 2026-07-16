"""
Tests for markdown converter.
"""

import pytest
from mdconvert.converter import MarkdownConverter
from mdconvert.patterns import PatternDetector


class TestPatternDetector:
    """Tests for pattern detection."""
    
    def setup_method(self):
        self.detector = PatternDetector()
    
    def test_detect_h1_first_line(self):
        result = self.detector.detect_header("My Document Title", {
            'line_number': 0,
            'prev_empty': False,
        })
        assert result is not None
        assert result.markdown == "# My Document Title"
        assert result.element_type == 'h1'
    
    def test_detect_h2_colon(self):
        result = self.detector.detect_header("Introduction:", {
            'line_number': 5,
            'prev_empty': True,
        })
        assert result is not None
        assert result.markdown == "## Introduction:"
        assert result.element_type == 'h2'
    
    def test_detect_h3_allcaps(self):
        result = self.detector.detect_header("IMPORTANT NOTES", {
            'line_number': 10,
            'prev_empty': True,
        })
        assert result is not None
        assert result.markdown == "### IMPORTANT NOTES"
        assert result.element_type == 'h3'
    
    def test_no_header_on_hashtag(self):
        result = self.detector.detect_header("# Already header", {
            'line_number': 5,
            'prev_empty': True,
        })
        assert result is None
    
    def test_detect_numbered_list(self):
        result = self.detector.detect_numbered_list("1. First item", {})
        assert result is not None
        assert result.markdown == "1. First item"
        assert result.element_type == 'numbered_list'
    
    def test_detect_task_list(self):
        result = self.detector.detect_task_list("[ ] Todo item", {})
        assert result is not None
        assert result.markdown == "- [ ] Todo item"
        assert result.element_type == 'task_list'
    
    def test_detect_task_list_checked(self):
        result = self.detector.detect_task_list("[x] Done item", {})
        assert result is not None
        assert result.markdown == "- [x] Done item"


class TestMarkdownConverter:
    """Tests for main converter."""
    
    def setup_method(self):
        self.converter = MarkdownConverter()
    
    def test_empty_input(self):
        result = self.converter.convert("")
        assert result.markdown == ""
        assert result.stats.original_chars == 0
    
    def test_basic_conversion(self):
        text = "My Title\nIntroduction:\nFirst point"
        result = self.converter.convert(text)
        assert "# My Title" in result.markdown
        assert "## Introduction:" in result.markdown
    
    def test_list_conversion(self):
        text = "Items:\n1. First\n2. Second\n- Bullet"
        result = self.converter.convert(text)
        assert "1. First" in result.markdown
        assert "2. Second" in result.markdown
        assert "- Bullet" in result.markdown
    
    def test_stats_calculation(self):
        text = "A" * 1000
        result = self.converter.convert(text)
        assert result.stats.original_chars == 1000
        assert result.stats.time_ms > 0
    
    def test_warnings_for_long_text(self):
        text = "A" * 500 + "\nB" * 500
        result = self.converter.convert(text)
        assert len(result.warnings) > 0