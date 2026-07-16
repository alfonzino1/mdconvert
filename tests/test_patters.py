"""
Tests for pattern detection module.
"""

import pytest
from mdconvert.patterns import PatternDetector, PatternMatch


class TestHeaderDetection:
    """Tests for header pattern detection."""
    
    def setup_method(self):
        self.detector = PatternDetector()
    
    def test_h1_first_line(self):
        """First line should become H1."""
        result = self.detector.detect_header("My Document Title", {
            'line_number': 0,
            'prev_empty': False,
        })
        assert result is not None
        assert result.markdown == "# My Document Title"
        assert result.element_type == 'h1'
        assert result.confidence == 0.9
    
    def test_h1_already_hashed(self):
        """Line starting with # should not be converted."""
        result = self.detector.detect_header("# Already a header", {
            'line_number': 0,
            'prev_empty': False,
        })
        assert result is None
    
    def test_h1_too_long(self):
        """Very long first line should not be H1."""
        long_text = "A" * 150
        result = self.detector.detect_header(long_text, {
            'line_number': 0,
            'prev_empty': False,
        })
        assert result is None
    
    def test_h2_colon_ending(self):
        """Line ending with colon should become H2."""
        result = self.detector.detect_header("Introduction:", {
            'line_number': 5,
            'prev_empty': True,
        })
        assert result is not None
        assert result.markdown == "## Introduction:"
        assert result.element_type == 'h2'
        assert result.confidence == 0.85
    
    def test_h2_colon_too_long(self):
        """Long line with colon should not be H2."""
        result = self.detector.detect_header("A" * 81 + ":", {
            'line_number': 5,
            'prev_empty': True,
        })
        assert result is None
    
    def test_h2_not_on_dash_line(self):
        """Line starting with dash should not be H2 even with colon."""
        result = self.detector.detect_header("- item: value", {
            'line_number': 5,
            'prev_empty': True,
        })
        assert result is None
    
    def test_h3_all_caps(self):
        """ALL CAPS line should become H3."""
        result = self.detector.detect_header("IMPORTANT SAFETY NOTES", {
            'line_number': 10,
            'prev_empty': True,
        })
        assert result is not None
        assert result.markdown == "### IMPORTANT SAFETY NOTES"
        assert result.element_type == 'h3'
        assert result.confidence == 0.8
    
    def test_h3_all_caps_with_number(self):
        """ALL CAPS with numbers should not be H3."""
        result = self.detector.detect_header("VERSION 2.0 RELEASE", {
            'line_number': 10,
            'prev_empty': True,
        })
        assert result is None
    
    def test_h3_all_caps_too_long(self):
        """Long ALL CAPS should not be H3."""
        result = self.detector.detect_header("A" * 61, {
            'line_number': 10,
            'prev_empty': True,
        })
        assert result is None
    
    def test_h4_numbered_section(self):
        """Numbered section like '1.2.3 Title' should become H4."""
        result = self.detector.detect_header("1.2.3 Implementation Details", {
            'line_number': 15,
            'prev_empty': True,
        })
        assert result is not None
        assert result.markdown == "#### 1.2.3 Implementation Details"
        assert result.element_type == 'h4'
    
    def test_h4_numbered_section_missing_title(self):
        """Number without text after should not be H4."""
        result = self.detector.detect_header("1.2.3", {
            'line_number': 15,
            'prev_empty': True,
        })
        assert result is None


class TestListDetection:
    """Tests for list pattern detection."""
    
    def setup_method(self):
        self.detector = PatternDetector()
    
    def test_numbered_list_dot(self):
        """Number with dot should be numbered list."""
        result = self.detector.detect_numbered_list("1. First item", {})
        assert result is not None
        assert result.markdown == "1. First item"
        assert result.element_type == 'numbered_list'
        assert result.confidence == 0.95
    
    def test_numbered_list_paren(self):
        """Number with parenthesis should be numbered list."""
        result = self.detector.detect_numbered_list("1) First item", {})
        assert result is not None
        assert result.markdown == "1. First item"
    
    def test_numbered_list_multiline(self):
        """Multi-digit numbers should work."""
        result = self.detector.detect_numbered_list("123. Item", {})
        assert result is not None
        assert result.markdown == "123. Item"
    
    def test_not_numbered_list(self):
        """Text that looks like a number but isn't."""
        result = self.detector.detect_numbered_list("2024 was a great year", {})
        assert result is None
    
    def test_bullet_list_dash(self):
        """Dash should be bullet list."""
        result = self.detector.detect_bullet_list("- Item", {})
        assert result is not None
        assert result.markdown == "- Item"
        assert result.element_type == 'bullet_list'
    
    def test_bullet_list_star(self):
        """Star should be bullet list."""
        result = self.detector.detect_bullet_list("* Item", {})
        assert result is not None
        assert result.markdown == "- Item"
    
    def test_bullet_list_plus(self):
        """Plus should be bullet list."""
        result = self.detector.detect_bullet_list("+ Item", {})
        assert result is not None
        assert result.markdown == "- Item"
    
    def test_bullet_list_letter_in_context(self):
        """Letter with paren in list context should be bullet."""
        result = self.detector.detect_bullet_list("a) Item", {
            'in_list': True,
        })
        assert result is not None
        assert result.markdown == "- Item"
        assert result.confidence == 0.6
    
    def test_not_bullet_without_context(self):
        """Letter with paren without context should not be bullet."""
        result = self.detector.detect_bullet_list("a) Item", {
            'in_list': False,
        })
        assert result is None
    
    def test_task_list_unchecked(self):
        """[ ] should be unchecked task."""
        result = self.detector.detect_task_list("[ ] Do something", {})
        assert result is not None
        assert result.markdown == "- [ ] Do something"
        assert result.element_type == 'task_list'
    
    def test_task_list_checked_lower(self):
        """[x] should be checked task."""
        result = self.detector.detect_task_list("[x] Done", {})
        assert result is not None
        assert result.markdown == "- [x] Done"
    
    def test_task_list_checked_upper(self):
        """[X] should be checked task."""
        result = self.detector.detect_task_list("[X] Done", {})
        assert result is not None
        assert result.markdown == "- [x] Done"


class TestSpecialElements:
    """Tests for code, quotes, links, tables."""
    
    def setup_method(self):
        self.detector = PatternDetector()
    
    def test_code_fence(self):
        """Triple backtick should be code fence."""
        result = self.detector.detect_code_block("```python", {})
        assert result is not None
        assert result.markdown == "```python"
        assert result.element_type == 'code_fence'
    
    def test_code_indented(self):
        """4-space indented text should be code block."""
        result = self.detector.detect_code_block("    print('hello')", {})
        assert result is not None
        assert result.markdown == "    print('hello')"
        assert result.element_type == 'code_block'
    
    def test_not_code_short_indent(self):
        """Short indented text should not be code."""
        result = self.detector.detect_code_block("    hi", {})
        assert result is None
    
    def test_blockquote_existing(self):
        """Existing blockquote should pass through."""
        result = self.detector.detect_blockquote("> quoted text", {})
        assert result is not None
        assert result.markdown == "> quoted text"
        assert result.confidence == 1.0
    
    def test_blockquote_quoted_text(self):
        """Text in double quotes should become blockquote."""
        result = self.detector.detect_blockquote(
            '"This is a long quoted passage that should be a blockquote"', 
            {}
        )
        assert result is not None
        assert result.element_type == 'blockquote'
    
    def test_blockquote_short_quote(self):
        """Short quoted text should not be blockquote."""
        result = self.detector.detect_blockquote('"Hi"', {})
        assert result is None
    
    def test_link_plain_url(self):
        """Plain URL should become autolink."""
        result = self.detector.detect_link("https://example.com", {})
        assert result is not None
        assert result.markdown == "<https://example.com>"
    
    def test_link_text_with_url(self):
        """Text followed by URL should become named link."""
        result = self.detector.detect_link(
            "Example Website https://example.com", 
            {}
        )
        assert result is not None
        assert result.markdown == "[Example Website](https://example.com)"
    
    def test_not_link_no_url(self):
        """Text without URL should not be link."""
        result = self.detector.detect_link("Just some text", {})
        assert result is None
    
    def test_horizontal_rule_dashes(self):
        """Three dashes should be horizontal rule."""
        result = self.detector.detect_horizontal_rule("---", {})
        assert result is not None
        assert result.markdown == "---"
    
    def test_horizontal_rule_stars(self):
        """Three stars should be horizontal rule."""
        result = self.detector.detect_horizontal_rule("***", {})
        assert result is not None
        assert result.markdown == "---"
    
    def test_horizontal_rule_spaced(self):
        """Spaced separators should be horizontal rule."""
        result = self.detector.detect_horizontal_rule("- - -", {})
        assert result is not None
        assert result.markdown == "---"
    
    def test_table_with_pipes(self):
        """Line with multiple pipes should be table."""
        result = self.detector.detect_table("| Name | Age | City |", {})
        assert result is not None
        assert result.element_type == 'table'
    
    def test_table_csv_like(self):
        """CSV-like line in context should be table."""
        result = self.detector.detect_table(
            "John,30,New York", 
            {'prev_has_commas': True}
        )
        assert result is not None
        assert result.markdown == "| John | 30 | New York |"
        assert result.element_type == 'table_row'
    
    def test_table_csv_no_context(self):
        """CSV-like line without context should not be table."""
        result = self.detector.detect_table(
            "John,30,New York", 
            {'prev_has_commas': False}
        )
        assert result is None


class TestDefinitionList:
    """Tests for definition list detection."""
    
    def setup_method(self):
        self.detector = PatternDetector()
    
    def test_definition_term_colon(self):
        """Term: definition pattern should work."""
        result = self.detector.detect_definition_list(
            "Status: All systems operational", 
            {'is_header': False}
        )
        assert result is not None
        assert result.markdown == "**Status**: All systems operational"
        assert result.element_type == 'definition'
    
    def test_definition_not_when_header(self):
        """Should not match when context says it's a header."""
        result = self.detector.detect_definition_list(
            "Status: All systems operational", 
            {'is_header': True}
        )
        assert result is None
    
    def test_definition_short_definition(self):
        """Short definition should not match."""
        result = self.detector.detect_definition_list(
            "Key: val", 
            {'is_header': False}
        )
        assert result is None


class TestDetectMethod:
    """Tests for the main detect method."""
    
    def setup_method(self):
        self.detector = PatternDetector()
    
    def test_detect_returns_first_match(self):
        """Should return first matching pattern."""
        result = self.detector.detect("# Header", {})
        assert result is None  # Headers with # already pass through
    
    def test_detect_header_match(self):
        """Should detect header."""
        result = self.detector.detect("Introduction:", {
            'line_number': 5,
            'prev_empty': True,
            'in_list': False,
            'in_code_block': False,
            'is_header': False,
            'prev_has_commas': False,
        })
        assert result is not None
        assert result.element_type == 'h2'
    
    def test_detect_no_match(self):
        """Should return None when no pattern matches."""
        result = self.detector.detect("just a normal line of text", {
            'line_number': 5,
            'prev_empty': False,
            'in_list': False,
            'in_code_block': False,
            'is_header': False,
            'prev_has_commas': False,
        })
        assert result is None


class TestEdgeCases:
    """Edge case tests."""
    
    def setup_method(self):
        self.detector = PatternDetector()
    
    def test_empty_line(self):
        """Empty lines should not match any pattern."""
        result = self.detector.detect("", {
            'line_number': 0,
            'prev_empty': True,
        })
        assert result is None
    
    def test_whitespace_only(self):
        """Whitespace-only lines should not match."""
        result = self.detector.detect("   ", {
            'line_number': 0,
            'prev_empty': True,
        })
        assert result is None
    
    def test_multiple_patterns_possible(self):
        """When multiple patterns could match, first wins."""
        # "1. Something:" could be numbered list or H2
        # Should pick the first detector in order (numbered list wins)
        result = self.detector.detect("1. Something:", {
            'line_number': 5,
            'prev_empty': True,
            'in_list': False,
            'in_code_block': False,
            'is_header': False,
            'prev_has_commas': False,
        })
        assert result is not None
        assert result.element_type == 'numbered_list'
    
    def test_special_characters_in_text(self):
        """Special characters should not break detection."""
        text = "Section with $pecial ch@racters:"
        result = self.detector.detect_header(text, {
            'line_number': 5,
            'prev_empty': True,
        })
        assert result is not None
        assert result.markdown == f"## {text}"
    
    def test_unicode_text(self):
        """Unicode should be handled correctly."""
        text = "Обновление проекта:"
        result = self.detector.detect_header(text, {
            'line_number': 5,
            'prev_empty': True,
        })
        assert result is not None
        assert result.markdown == f"## {text}"
    
    def test_emoji_in_text(self):
        """Emoji should not break detection."""
        text = "Launch 🚀:"
        result = self.detector.detect_header(text, {
            'line_number': 5,
            'prev_empty': True,
        })
        assert result is not None
        assert result.markdown == f"## {text}"