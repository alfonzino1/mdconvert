"""
Rich CLI interface.
"""

import sys
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich import box

from .converter import MarkdownConverter
from .config import Config
from .templates import TEMPLATES, TEMPLATE_NAMES

console = Console()
config = Config()


@click.group()
@click.version_option(version="1.0.0", prog_name="mdconvert")
def cli():
    """⚡ Smart Markdown Converter
    
    Convert plain text to optimized Markdown for Claude and other LLMs.
    Save tokens, improve formatting, automate your workflow.
    """
    pass


@cli.command()
@click.argument('file', type=click.Path(exists=True), required=False)
@click.option('-t', '--text', help='Convert text directly')
@click.option('-o', '--output', type=click.Path(), help='Save to file')
@click.option('-c', '--copy', is_flag=True, help='Copy to clipboard')
@click.option('-s', '--stats', is_flag=True, help='Show detailed statistics')
@click.option('--no-smart', is_flag=True, help='Disable smart detection')
@click.option('-f', '--format', type=click.Choice(['claude', 'github', 'standard']),
              default='claude', help='Output format style')
def convert(file, text, output, copy, stats, no_smart, format):
    """Convert text to Markdown."""
    
    # Get input
    if file:
        with console.status(f"[cyan]Reading {file}..."):
            input_text = Path(file).read_text(encoding='utf-8')
    elif text:
        input_text = text
    elif not sys.stdin.isatty():
        input_text = sys.stdin.read()
    else:
        console.print("[yellow]✏️  Enter text (Ctrl+D to finish):[/yellow]")
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            input_text = '\n'.join(lines)
    
    if not input_text or not input_text.strip():
        console.print("[red]❌ No text provided[/red]")
        return
    
    # Convert
    with console.status("[cyan]Converting...[/cyan]") as status:
        converter = MarkdownConverter(format_style=format)
        result = converter.convert(input_text, smart=not no_smart)
        status.update("[green]Done![/green]")
    
    # Output
    if output:
        Path(output).write_text(result.markdown, encoding='utf-8')
        console.print(f"[green]✅ Saved to {output}[/green]")
    else:
        console.print()
        console.print(Panel(
            Syntax(result.markdown, "markdown", theme="monokai", 
                   line_numbers=False, word_wrap=True),
            title="[bold]Markdown Output[/bold]",
            border_style="green",
            padding=(1, 2),
        ))
    
    # Copy
    if copy:
        try:
            import pyperclip
            pyperclip.copy(result.markdown)
            console.print("[green]📋 Copied to clipboard![/green]")
        except ImportError:
            console.print("[yellow]⚠️  Install pyperclip for clipboard support[/yellow]")
    
    # Stats
    if stats or config.get('stats'):
        _show_stats(result)
    
    # Warnings
    if result.warnings:
        console.print()
        for warning in result.warnings:
            console.print(f"[yellow]💡 {warning}[/yellow]")


@cli.command()
@click.argument('text', nargs=-1)
@click.option('-c', '--copy', is_flag=True, help='Copy to clipboard')
def quick(text, copy):
    """Quick convert from command line."""
    if not text:
        console.print("[red]❌ No text provided[/red]")
        return
    
    input_text = ' '.join(text)
    converter = MarkdownConverter()
    result = converter.convert(input_text)
    
    console.print(f"\n[green]{result.markdown}[/green]\n")
    
    if copy:
        try:
            import pyperclip
            pyperclip.copy(result.markdown)
            console.print("[dim]📋 Copied[/dim]")
        except ImportError:
            pass


@cli.command()
@click.argument('template_name', type=click.Choice(TEMPLATE_NAMES))
@click.option('-d', '--data', multiple=True, help='Template variables (key=value)')
def template(template_name, data):
    """Generate from template."""
    template_text = TEMPLATES.get(template_name)
    
    if not template_text:
        console.print(f"[red]❌ Template '{template_name}' not found[/red]")
        return
    
    # Parse variables
    variables = {}
    for item in data:
        if '=' in item:
            key, value = item.split('=', 1)
            variables[key] = value
    
    # Fill template
    try:
        filled = template_text.format(**variables)
    except KeyError as e:
        console.print(f"[yellow]⚠️  Missing variable: {e}[/yellow]")
        console.print("[dim]Use -d key=value to provide variables[/dim]")
        return
    
    # Convert the filled template
    converter = MarkdownConverter()
    result = converter.convert(filled)
    
    console.print()
    console.print(Panel(
        Syntax(result.markdown, "markdown", theme="monokai"),
        title=f"[bold]Template: {template_name}[/bold]",
        border_style="blue",
    ))


@cli.command()
def list_templates():
    """List available templates."""
    table = Table(title="Available Templates", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Variables", style="green")
    
    for name, template in TEMPLATES.items():
        # Extract variables from template
        import re
        vars_found = re.findall(r'\{(\w+)\}', template)
        table.add_row(name, ", ".join(vars_found))
    
    console.print(table)


@cli.command()
@click.option('-p', '--port', type=int, default=8000, help='Port to listen on')
@click.option('--host', default='127.0.0.1', help='Host to bind to')
def watch_clipboard(port, host):
    """Watch clipboard for auto-conversion."""
    console.print("[cyan]👁️  Watching clipboard (Ctrl+C to stop)[/cyan]")
    console.print("[dim]Copy any text → auto-convert → result in clipboard[/dim]\n")
    
    try:
        import pyperclip
    except ImportError:
        console.print("[red]❌ Install pyperclip[/red]")
        return
    
    recent = ""
    converter = MarkdownConverter()
    count = 0
    
    try:
        while True:
            current = pyperclip.paste()
            if current != recent and len(current.strip()) > 10:
                count += 1
                console.print(f"[dim]#{count}[/dim] [cyan]Converting ({len(current)} chars)...[/cyan]", end=' ')
                
                result = converter.convert(current)
                pyperclip.copy(result.markdown)
                
                console.print(f"[green]✅ {len(result.markdown)} chars, ~{result.stats.tokens_saved} tokens saved[/green]")
                recent = result.markdown
            
            time.sleep(1)
    except KeyboardInterrupt:
        console.print(f"\n[yellow]👋 Stopped. Converted {count} texts.[/yellow]")


@cli.command()
def init():
    """Initialize config file."""
    config_path = Path.cwd() / '.mdconvert.yaml'
    
    if config_path.exists():
        console.print("[yellow]Config already exists[/yellow]")
        if not click.confirm("Overwrite?"):
            return
    
    config.save(config_path)
    console.print(f"[green]✅ Created {config_path}[/green]")


def _show_stats(result):
    """Display conversion statistics."""
    s = result.stats
    
    console.print()
    table = Table(title="📊 Conversion Statistics", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Detail", style="dim")
    
    table.add_row(
        "Characters", 
        f"{s.original_chars:,} → {s.markdown_chars:,}",
        f"{s.compression_ratio:.1%} compression"
    )
    table.add_row(
        "Tokens Saved",
        f"~{s.tokens_saved:,}",
        "Estimated for Claude"
    )
    table.add_row(
        "Processing Time",
        f"{s.time_ms:.1f}ms",
        ""
    )
    table.add_row(
        "Elements Found",
        f"Headers: {s.elements.headers}",
        f"Lists: {s.elements.lists}, Tasks: {s.elements.tasks}"
    )
    table.add_row(
        "Special Elements",
        f"Code: {s.elements.code_blocks}",
        f"Links: {s.elements.links}, Tables: {s.elements.tables}"
    )
    
    console.print(table)


if __name__ == '__main__':
    cli()