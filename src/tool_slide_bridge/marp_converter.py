"""
MARP converter module for tool-slide-bridge.

This module provides functionality to convert markdown content (especially from Claude)
into PowerPoint presentations using MARP CLI.
"""

import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator


class MarpConfig(BaseModel):
    """Configuration for MARP conversion."""

    theme: str = Field(default="corporate", description="MARP theme to use")
    paginate: bool = Field(default=True, description="Enable pagination")
    background_color: str = Field(default="#ffffff", description="Background color")
    color: str = Field(default="#2c3e50", description="Text color")
    enable_html: bool = Field(default=True, description="Enable HTML in markdown")
    pdf_outlines: bool = Field(default=True, description="Enable PDF outlines")


class ConversionResult(BaseModel):
    """Result of MARP conversion."""

    success: bool = Field(description="Whether conversion was successful")
    output_path: Optional[str] = Field(default=None, description="Path to output file")
    error_message: Optional[str] = Field(
        default=None, description="Error message if failed"
    )
    markdown_path: Optional[str] = Field(
        default=None, description="Path to intermediate markdown"
    )


class ClaudeToMarpConverter:
    """Convert Claude's markdown/HTML output to PowerPoint using MARP."""

    def __init__(
        self,
        template_dir: str = "templates",
        output_dir: str = "presentations",
        theme_dir: str = "themes",
    ):
        """
        Initialize the MARP converter.

        Args:
            template_dir: Directory containing PowerPoint templates
            output_dir: Directory for generated presentations
            theme_dir: Directory containing MARP themes
        """
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.theme_dir = Path(theme_dir)

        # Create directories if they don't exist
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.theme_dir.mkdir(parents=True, exist_ok=True)

    def process_claude_content(
        self,
        content: str,
        title: str = "presentation",
        config: Optional[MarpConfig] = None,
    ) -> str:
        """
        Convert Claude's markdown/HTML to MARP-compatible markdown.

        Args:
            content: Raw content from Claude
            title: Title for the presentation
            config: MARP configuration options

        Returns:
            MARP-compatible markdown content
        """
        if content is None:
            raise ValueError("Content cannot be None")

        if config is None:
            config = MarpConfig()

        # Add MARP directives
        marp_content = self._add_marp_directives(content, config)

        # Clean and structure content
        marp_content = self._structure_slides(marp_content)

        # Apply custom styling
        marp_content = self._apply_styling(marp_content)

        return marp_content

    def _add_marp_directives(self, content: str, config: MarpConfig) -> str:
        """
        Add MARP front matter and directives.

        Args:
            content: Original markdown content
            config: MARP configuration

        Returns:
            Content with MARP front matter
        """
        # Check if custom theme CSS exists
        theme_path = self.theme_dir / f"{config.theme}.css"
        theme_directive = (
            f"theme: {config.theme}" if theme_path.exists() else "theme: default"
        )

        # Build directives list for cleaner formatting
        directives = [
            "marp: true",
            theme_directive,
            f"paginate: {str(config.paginate).lower()}",
            f"backgroundColor: {config.background_color}",
            f"color: {config.color}",
        ]
        if config.enable_html:
            directives.append("html: true")
        if config.pdf_outlines:
            directives.append("pdf.outlines: true")

        # Filter out any falsy entries before joining
        directives = [d for d in directives if d]
        header = f"---\n" + "\n".join(directives) + "\n---\n\n"

        return header + content

    def _structure_slides(self, content: str) -> str:
        """
        Convert content structure to MARP slide breaks.

        Args:
            content: Markdown content

        Returns:
            Content with proper slide breaks
        """
        # Replace HTML slide breaks with MARP breaks
        content = re.sub(r"<hr[^>]*/?>", "\n---\n", content, flags=re.IGNORECASE)

        # Ensure level 1 and 2 headings create new slides
        # But not if they're immediately after a slide break
        lines = content.split("\n")
        result_lines = []

        for i, line in enumerate(lines):
            # Check if this is a heading
            if re.match(r"^#{1,2}\s", line):
                # Check if previous non-empty line is not a slide break
                prev_line_idx = i - 1
                while prev_line_idx >= 0 and not lines[prev_line_idx].strip():
                    prev_line_idx -= 1

                if prev_line_idx >= 0 and lines[prev_line_idx].strip() != "---":
                    result_lines.append("---")

            result_lines.append(line)

        content = "\n".join(result_lines)

        # Clean up extra breaks
        content = re.sub(r"\n---\n---\n", "\n---\n", content)
        content = re.sub(r"^---\n", "", content)  # Remove leading break

        return content

    def _apply_styling(self, content: str) -> str:
        """
        Apply MARP-specific styling directives.

        Args:
            content: Markdown content

        Returns:
            Content with styling directives
        """
        # Split into slides
        slides = content.split("---")
        styled_slides = []

        for i, slide in enumerate(slides):
            slide = slide.strip()
            if not slide:
                continue

            # Skip the front matter
            if i == 0 and slide.startswith("marp:"):
                styled_slides.append(slide)
                continue

            # Check slide content type and add appropriate class
            if re.search(r"^#\s", slide, re.MULTILINE):  # Title slide
                slide = "<!-- _class: lead -->\n\n" + slide
            elif re.search(r"```", slide):  # Code slide
                slide = "<!-- _class: code -->\n\n" + slide
            elif slide.count("\n") > 10:  # Content-heavy slide
                slide = "<!-- _class: dense -->\n\n" + slide

            styled_slides.append(slide)

        return "\n\n---\n\n".join(styled_slides)

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and invalid characters.

        Args:
            filename: Raw filename

        Returns:
            Sanitized filename
        """
        # Remove path separators and parent directory references
        filename = os.path.basename(filename)
        filename = filename.replace("..", "")

        # Remove invalid characters for filenames
        invalid_chars = '<>:"|?*\\/\x00'
        for char in invalid_chars:
            filename = filename.replace(char, "")

        # Remove leading/trailing dots and whitespace
        filename = filename.strip(". ")

        # Ensure filename is not empty
        if not filename:
            filename = "presentation"

        return filename
    def generate_presentation(
        self,
        content: str,
        filename: str = "presentation",
        output_format: str = "pptx",
        config: Optional[MarpConfig] = None,
    ) -> ConversionResult:
        """
        Generate PowerPoint from Claude content.

        Args:
            content: Raw content from Claude
            filename: Output filename (without extension)
            output_format: Output format (pptx, pdf, html)
            config: MARP configuration

        Returns:
            ConversionResult with status and output path
        """
        try:
            # Sanitize filename to prevent security issues
            filename = self._sanitize_filename(filename)

            # Validate output format
            valid_formats = ["pptx", "pdf", "html"]
            if output_format not in valid_formats:
                return ConversionResult(
                    success=False,
                    error_message=f"Invalid output format: {output_format}. Must be one of {valid_formats}",
                )

            # Process content
            marp_content = self.process_claude_content(content, title=filename, config=config)

            # Save markdown file
            md_file = self.output_dir / f"{filename}.md"
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(marp_content)

            # Generate output using MARP CLI
            output_file = self.output_dir / f"{filename}.{output_format}"

            # Build MARP command
            cmd = ["marp", str(md_file)]

            # Add format-specific options
            if output_format == "pptx":
                cmd.extend(["--pptx"])
            elif output_format == "pdf":
                cmd.extend(["--pdf"])
            elif output_format == "html":
                cmd.extend(["--html"])

            # Add output path
            cmd.extend(["--output", str(output_file)])

            # Add theme directory if custom themes exist
            if any(self.theme_dir.glob("*.css")):
                cmd.extend(["--theme-set", str(self.theme_dir)])

            # Run MARP conversion
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            return ConversionResult(
                success=True, output_path=str(output_file), markdown_path=str(md_file)
            )

        except subprocess.CalledProcessError as e:
            error_msg = f"MARP conversion failed: {e.stderr or e.stdout or str(e)}"
            return ConversionResult(
                success=False,
                error_message=error_msg,
                markdown_path=str(md_file) if "md_file" in locals() else None,
            )
        except Exception as e:
            return ConversionResult(
                success=False, error_message=f"Unexpected error: {str(e)}"
            )

    def check_marp_installation(self) -> bool:
        """
        Check if MARP CLI is installed and accessible.

        Returns:
            True if MARP is installed, False otherwise
        """
        try:
            result = subprocess.run(
                ["marp", "--version"], capture_output=True, text=True, check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_available_themes(self) -> list[str]:
        """
        Get list of available themes.

        Returns:
            List of theme names
        """
        themes = ["default", "gaia", "uncover"]  # Built-in MARP themes

        # Add custom themes from theme directory
        if self.theme_dir.exists():
            custom_themes = [p.stem for p in self.theme_dir.glob("*.css")]
            themes.extend(custom_themes)

        return themes
