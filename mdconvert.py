#!/usr/bin/env python3
"""
Markdown Converter MVP
Quick text-to-markdown conversion for Claude token optimization.
"""

import re
import sys
from pathlib import Path
from typing import Optional
import click

# ============================================================
# CONVERTER ENGINE
# ============================================================

class MarkdownConverter:
    """Converts plain text to optimized Markdown."""
    
    def convert(self, text: str) -> str:
        """Convert text to Markdown with smart detection."""
        if not text.strip():
            return ""
        
        lines = text.split('\n')
        result = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if not stripped:
                result.append('')
                continue
            
            # First line = main title
            if i == 0 and len(stripped) < 100 and not stripped.startswith('#'):
                result.append(f"# {stripped}")
                continue
            
            # Lines ending with ":" = section headers
            if stripped.endswith(':') and len(stripped) < 80 and not stripped.startswith('#'):
                result.append(f"## {stripped}")
                continue
            
            # ALL CAPS lines = subheaders
            if (stripped.isupper() and len(stripped) < 60 
                and not stripped.startswith('#') and not any(c.isdigit() for c in stripped)):
                result.append(f"### {stripped}")
                continue
            
            # Numbered items
            if re.match(r'^\d+[\.\)]', stripped):
                match = re.match(r'^(\d+)[\.\)]\s*(.+)', stripped)
                if match:
                    result.append(f"{match.group(1)}. {match.group(2)}")
                    continue
            
            # Bullet items
            if stripped.startswith(('-', '*', '+')):
                result.append(f"- {stripped[1:].strip()}")
                continue
            
            result.append(line)
        
        text = '\n'.join(result)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def get_stats(self, original: str, markdown: str) -> dict:
        """Calculate conversion statistics."""
        original_tokens = int(len(original.split()) * 1.3)
        markdown_tokens = int(len(markdown.split()) * 1.3)
        tokens_saved = max(0, original_tokens - markdown_tokens)
        
        return {
            'original_chars': len(original),
            'markdown_chars': len(markdown),
            'tokens_saved': tokens_saved,
            'compression': f"{(1 - len(markdown) / len(original)) * 100:.1f}%" if original else "0%"
        }


# ============================================================
# CLI
# ============================================================

converter = MarkdownConverter()

@click.group()
def cli():
    """⚡ Markdown Converter — save tokens in Claude"""
    pass

@cli.command()
@click.argument('file', type=click.Path(exists=True), required=False)
@click.option('-t', '--text', help='Convert text directly')
@click.option('-o', '--output', type=click.Path(), help='Save to file')
@click.option('-c', '--copy', is_flag=True, help='Copy to clipboard')
@click.option('-s', '--stats', is_flag=True, help='Show statistics')
def convert(file: Optional[str], text: Optional[str], output: Optional[str], 
            copy: bool, stats: bool):
    """Convert text to Markdown"""
    
    # Get input
    if file:
        input_text = Path(file).read_text(encoding='utf-8')
        click.echo(f"📄 {file}")
    elif text:
        input_text = text
    elif not sys.stdin.isatty():
        input_text = sys.stdin.read()
    else:
        click.echo("✏️  Paste your text (Ctrl+D to finish):")
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            input_text = '\n'.join(lines)
    
    if not input_text.strip():
        click.echo("❌ No text provided")
        return
    
    # Convert
    result = converter.convert(input_text)
    
    # Output
    if output:
        Path(output).write_text(result, encoding='utf-8')
        click.echo(f"✅ {output}")
    else:
        click.echo(f"\n{'='*60}")
        click.echo(result)
        click.echo(f"{'='*60}\n")
    
    # Copy
    if copy:
        try:
            import pyperclip
            pyperclip.copy(result)
            click.echo("📋 Copied!")
        except ImportError:
            click.echo("⚠️  Install pyperclip for clipboard support")
    
    # Stats
    if stats:
        s = converter.get_stats(input_text, result)
        click.echo(f"\n📊 Stats:")
        click.echo(f"   Chars: {s['original_chars']} → {s['markdown_chars']} ({s['compression']})")
        click.echo(f"   Tokens saved: ~{s['tokens_saved']}")

@cli.command()
@click.argument('text', nargs=-1)
def quick(text: tuple):
    """Quick: mdconvert quick your text here"""
    input_text = ' '.join(text)
    result = converter.convert(input_text)
    
    click.echo(result)
    
    try:
        import pyperclip
        pyperclip.copy(result)
        click.echo("\n📋 Copied!", err=True)
    except ImportError:
        pass

@cli.command()
def watch():
    """Watch clipboard and auto-convert"""
    click.echo("👁️  Watching clipboard (Ctrl+C to stop)...")
    click.echo("   Copy text → auto-convert → result in clipboard\n")
    
    try:
        import pyperclip
        import time
        
        recent = ""
        while True:
            try:
                current = pyperclip.paste()
                if current != recent and len(current) > 10:
                    click.echo(f"\n🔄 Converting ({len(current)} chars)...")
                    result = converter.convert(current)
                    pyperclip.copy(result)
                    click.echo(f"✅ Done! ({len(result)} chars)")
                    recent = result
                time.sleep(1)
            except KeyboardInterrupt:
                break
    except ImportError:
        click.echo("❌ Install pyperclip: pip install pyperclip")
        return
    
    click.echo("\n👋 Stopped")

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == '__main__':
    cli()