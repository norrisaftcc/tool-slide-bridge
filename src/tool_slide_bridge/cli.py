"""
Command-line interface for tool-slide-bridge.
"""

import random
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .marp_converter import ClaudeToMarpConverter, MarpConfig

console = Console()

# Fortune-style messages for the startup banner
FORTUNE_MESSAGES = [
    "To be, rather than to seem",
    "Esse quam videri",
    "Claude says hi",
    "AI to PowerPoint without friction",
    "Transforming thoughts into slides",
    "Your AI presentation assistant",
    "Making presentations magical ✨",
    "Slide into success",
    "Powered by MARP and imagination",
]

# Pad messages to consistent length for better visual alignment
FORTUNE_MESSAGES = [msg.center(37) for msg in FORTUNE_MESSAGES]


def print_banner() -> None:
    """Print the tool banner with a rotating fortune message."""
    fortune = random.choice(FORTUNE_MESSAGES)

    # Messages are already padded to 37 chars, just add borders
    fortune_line = f"║{fortune}║"

    banner = f"""
╔═══════════════════════════════════════╗
║        Tool: Slide Bridge 🌉          ║
{fortune_line}
╚═══════════════════════════════════════╝
"""
    console.print(banner, style="bold blue")


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    default="presentation",
    help="Output filename (without extension)"
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["pptx", "pdf", "html"]),
    default="pptx",
    help="Output format",
)
@click.option("-t", "--theme", default="corporate", help="MARP theme to use")
@click.option("--no-paginate", is_flag=True, help="Disable slide pagination")
@click.option("--bg-color", default="#ffffff", help="Background color")
@click.option("--text-color", default="#2c3e50", help="Text color")
@click.option("--check-marp", is_flag=True, help="Check MARP CLI installation")
@click.option("--list-themes", is_flag=True, help="List available themes")
def main(
    input_file: str,
    output: str,
    format: str,
    theme: str,
    no_paginate: bool,
    bg_color: str,
    text_color: str,
    check_marp: bool,
    list_themes: bool,
) -> None:
    """
    Convert Claude's markdown output to PowerPoint presentations.

    INPUT_FILE: Path to markdown file containing Claude's output
    """
    print_banner()

    # Initialize converter
    converter = ClaudeToMarpConverter()

    # Handle utility commands
    if check_marp:
        if converter.check_marp_installation():
            console.print("✅ MARP CLI is installed and ready!", style="green")
        else:
            console.print("❌ MARP CLI is not installed!", style="red")
            console.print("\nTo install MARP CLI, run:", style="yellow")
            console.print("  npm install -g @marp-team/marp-cli", style="cyan")
        return

    if list_themes:
        themes = converter.get_available_themes()
        table = Table(title="Available Themes")
        table.add_column("Theme Name", style="cyan")
        table.add_column("Type", style="green")

        for theme_name in themes:
            theme_type = (
                "Built-in"
                if theme_name in ["default", "gaia", "uncover"]
                else "Custom"
            )
            table.add_row(theme_name, theme_type)

        console.print(table)
        return

    # Check MARP installation before proceeding
    if not converter.check_marp_installation():
        console.print("❌ Error: MARP CLI is not installed!", style="red")
        console.print("\nTo install MARP CLI, run:", style="yellow")
        console.print("  npm install -g @marp-team/marp-cli", style="cyan")
        sys.exit(1)

    # Read input file
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()

        console.print(
            f"📄 Read {len(content)} characters from {input_file}", style="dim"
        )

    except Exception as e:
        console.print(f"❌ Error reading input file: {e}", style="red")
        sys.exit(1)

    # Configure MARP
    config = MarpConfig(
        theme=theme,
        paginate=not no_paginate,
        background_color=bg_color,
        color=text_color,
    )

    # Show configuration
    console.print("\n⚙️  Configuration:", style="bold")
    console.print(f"  Theme: {config.theme}")
    console.print(f"  Format: {format.upper()}")
    pagination_status = "Enabled" if config.paginate else "Disabled"
    console.print(f"  Pagination: {pagination_status}")

    # Convert with progress
    console.print("\n🔄 Converting to PowerPoint...", style="bold cyan")

    with console.status("Processing content..."):
        result = converter.generate_presentation(
            content=content,
            filename=output,
            output_format=format,
            config=config
        )

    # Show result
    if result.success:
        console.print("\n✅ Success!", style="bold green")

        output_panel = Panel(
            f"[bold cyan]Output:[/bold cyan] {result.output_path}\n"
            f"[bold cyan]Markdown:[/bold cyan] {result.markdown_path}",
            title="Generated Files",
            border_style="green",
        )
        console.print(output_panel)

        console.print("\n🎯 Next steps:", style="bold")
        console.print("  1. Open the generated file in PowerPoint")
        console.print("  2. Review and customize as needed")
        console.print("  3. Use the markdown file for future edits")

    else:
        console.print(
            f"\n❌ Conversion failed: {result.error_message}", style="red"
        )

        if result.markdown_path:
            console.print(
                f"\n💡 Intermediate markdown saved to: "
                f"{result.markdown_path}",
                style="yellow",
            )
            console.print(
                "   You can manually run MARP on this file to debug "
                "the issue.",
                style="dim",
            )

        sys.exit(1)


if __name__ == "__main__":
    main()
