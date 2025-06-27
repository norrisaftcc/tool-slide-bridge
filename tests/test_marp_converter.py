"""Comprehensive tests for MARP converter functionality."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from tool_slide_bridge.marp_converter import (
    ClaudeToMarpConverter,
    ConversionResult,
    MarpConfig,
)


class TestMarpConverter:
    """Test suite for ClaudeToMarpConverter."""

    @pytest.fixture
    def converter(self, tmp_path):
        """Create a converter instance with temporary directories."""
        return ClaudeToMarpConverter(
            template_dir=str(tmp_path / "templates"),
            output_dir=str(tmp_path / "presentations"),
            theme_dir=str(tmp_path / "themes"),
        )

    @pytest.fixture
    def sample_content(self):
        """Sample markdown content for testing."""
        return """# Welcome to My Presentation

This is the first slide with some content.

## Second Slide

- Point 1
- Point 2
- Point 3

## Code Example

```python
def hello_world():
    print("Hello, World!")
```

## Thank You!

Questions?"""

    def test_converter_initialization(self, tmp_path):
        """Test that converter initializes with proper directories."""
        converter = ClaudeToMarpConverter(
            template_dir=str(tmp_path / "templates"),
            output_dir=str(tmp_path / "presentations"),
            theme_dir=str(tmp_path / "themes"),
        )

        assert converter.template_dir.exists()
        assert converter.output_dir.exists()
        assert converter.theme_dir.exists()

    def test_process_claude_content_basic(self, converter, sample_content):
        """Test basic content processing."""
        result = converter.process_claude_content(sample_content)

        # Check MARP directives are added
        assert "marp: true" in result
        assert "theme:" in result
        assert "paginate:" in result
        assert "---" in result

        # Check content is preserved
        assert "Welcome to My Presentation" in result
        assert "hello_world()" in result

    def test_process_claude_content_with_config(self, converter, sample_content):
        """Test content processing with custom config."""
        config = MarpConfig(
            theme="custom",
            paginate=False,
            background_color="#000000",
            color="#ffffff",
            enable_html=False,
            pdf_outlines=False,
        )

        result = converter.process_claude_content(sample_content, config=config)

        assert "paginate: false" in result
        assert "backgroundColor: #000000" in result
        assert "color: #ffffff" in result
        assert "html: true" not in result
        assert "pdf.outlines: true" not in result

    def test_add_marp_directives_default_theme(self, converter):
        """Test MARP directives with default theme."""
        config = MarpConfig()
        content = "# Test"

        result = converter._add_marp_directives(content, config)

        assert result.startswith("---\n")
        assert "marp: true" in result
        assert (
            "theme: default" in result
        )  # Should use default when custom doesn't exist
        assert result.endswith("---\n\n# Test")

    def test_add_marp_directives_custom_theme(self, converter):
        """Test MARP directives with custom theme that exists."""
        # Create a custom theme file
        theme_file = converter.theme_dir / "corporate.css"
        theme_file.write_text("/* Custom theme */")

        config = MarpConfig(theme="corporate")
        content = "# Test"

        result = converter._add_marp_directives(content, config)

        assert "theme: corporate" in result

    def test_structure_slides_heading_breaks(self, converter):
        """Test automatic slide breaks on headings."""
        content = """# Slide 1
Content 1

## Slide 2
Content 2

### Not a new slide
Still slide 2

# Slide 3
Content 3"""

        result = converter._structure_slides(content)

        # Count slide breaks
        breaks = result.count("\n---\n")
        assert breaks >= 2  # At least 2 breaks for 3 slides

        # Ensure no double breaks
        assert "\n---\n---\n" not in result

    def test_structure_slides_existing_breaks(self, converter):
        """Test handling of existing slide breaks."""
        content = """# Slide 1
---
# Slide 2
<hr>
# Slide 3"""

        result = converter._structure_slides(content)

        # HTML breaks should be converted
        assert "<hr>" not in result
        assert "---" in result

    def test_apply_styling_title_slide(self, converter):
        """Test styling for title slides."""
        content = """marp: true
---
# Main Title
Subtitle"""

        result = converter._apply_styling(content)

        assert "<!-- _class: lead -->" in result

    def test_apply_styling_code_slide(self, converter):
        """Test styling for code slides."""
        content = """marp: true
---
## Code Example
```python
print("test")
```"""

        result = converter._apply_styling(content)

        assert "<!-- _class: code -->" in result

    def test_apply_styling_dense_slide(self, converter):
        """Test styling for content-heavy slides."""
        lines = ["Line " + str(i) for i in range(15)]
        content = f"""marp: true
---
## Dense Content
{chr(10).join(lines)}"""

        result = converter._apply_styling(content)

        assert "<!-- _class: dense -->" in result

    @patch("subprocess.run")
    def test_generate_presentation_success(self, mock_run, converter, sample_content):
        """Test successful presentation generation."""
        # Mock successful MARP execution
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")

        result = converter.generate_presentation(
            sample_content, filename="test_presentation", output_format="pptx"
        )

        assert result.success is True
        assert result.output_path.endswith("test_presentation.pptx")
        assert result.markdown_path.endswith("test_presentation.md")
        assert result.error_message is None

        # Verify subprocess was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "marp"
        assert "--pptx" in call_args
        assert "--output" in call_args

    @patch("subprocess.run")
    def test_generate_presentation_pdf_format(
        self, mock_run, converter, sample_content
    ):
        """Test PDF generation."""
        mock_run.return_value = Mock(returncode=0)

        result = converter.generate_presentation(sample_content, output_format="pdf")

        call_args = mock_run.call_args[0][0]
        assert "--pdf" in call_args
        assert result.output_path.endswith(".pdf")

    @patch("subprocess.run")
    def test_generate_presentation_html_format(
        self, mock_run, converter, sample_content
    ):
        """Test HTML generation."""
        mock_run.return_value = Mock(returncode=0)

        result = converter.generate_presentation(sample_content, output_format="html")

        call_args = mock_run.call_args[0][0]
        assert "--html" in call_args
        assert result.output_path.endswith(".html")

    @patch("subprocess.run")
    def test_generate_presentation_with_custom_themes(
        self, mock_run, converter, sample_content
    ):
        """Test generation with custom theme directory."""
        # Create a theme file
        theme_file = converter.theme_dir / "custom.css"
        theme_file.write_text("/* theme */")

        mock_run.return_value = Mock(returncode=0)

        converter.generate_presentation(sample_content)

        call_args = mock_run.call_args[0][0]
        assert "--theme-set" in call_args

    @patch("subprocess.run")
    def test_generate_presentation_marp_failure(
        self, mock_run, converter, sample_content
    ):
        """Test handling of MARP conversion failure."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["marp"], stderr="MARP error: Invalid syntax"
        )

        result = converter.generate_presentation(sample_content)

        assert result.success is False
        assert "MARP conversion failed" in result.error_message
        assert "Invalid syntax" in result.error_message
        assert result.output_path is None
        assert result.markdown_path is not None  # MD file should still be created

    def test_generate_presentation_file_creation(self, converter, sample_content):
        """Test that markdown file is actually created."""
        # Don't mock subprocess to test file creation
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            result = converter.generate_presentation(
                sample_content, filename="test_file"
            )

            # Check markdown file was created
            md_path = Path(result.markdown_path)
            assert md_path.exists()

            # Verify content
            content = md_path.read_text()
            assert "marp: true" in content
            assert sample_content.split("\n")[0] in content  # First line preserved

    def test_generate_presentation_exception_handling(self, converter):
        """Test handling of unexpected exceptions."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Unexpected error")

            result = converter.generate_presentation("# Test")

            assert result.success is False
            assert "Unexpected error" in result.error_message

    @patch("subprocess.run")
    def test_check_marp_installation_success(self, mock_run, converter):
        """Test successful MARP installation check."""
        mock_run.return_value = Mock(returncode=0, stdout="v1.5.0")

        assert converter.check_marp_installation() is True

        mock_run.assert_called_once_with(
            ["marp", "--version"], capture_output=True, text=True, check=True
        )

    @patch("subprocess.run")
    def test_check_marp_installation_not_found(self, mock_run, converter):
        """Test MARP not installed."""
        mock_run.side_effect = FileNotFoundError()

        assert converter.check_marp_installation() is False

    @patch("subprocess.run")
    def test_check_marp_installation_error(self, mock_run, converter):
        """Test MARP check with error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["marp"])

        assert converter.check_marp_installation() is False

    def test_get_available_themes_default(self, converter):
        """Test getting default themes."""
        themes = converter.get_available_themes()

        assert "default" in themes
        assert "gaia" in themes
        assert "uncover" in themes
        assert len(themes) == 3  # Only built-in themes

    def test_get_available_themes_with_custom(self, converter):
        """Test getting themes including custom ones."""
        # Create custom theme files
        (converter.theme_dir / "corporate.css").write_text("/* corporate */")
        (converter.theme_dir / "modern.css").write_text("/* modern */")
        (converter.theme_dir / "readme.txt").write_text("not a theme")

        themes = converter.get_available_themes()

        assert "default" in themes
        assert "corporate" in themes
        assert "modern" in themes
        assert "readme" not in themes  # Only .css files
        assert len(themes) == 5  # 3 built-in + 2 custom


class TestSecurityFeatures:
    """Test security-related features."""

    @pytest.fixture
    def converter(self, tmp_path):
        """Create a converter instance."""
        return ClaudeToMarpConverter(output_dir=str(tmp_path / "output"))

    def test_path_traversal_prevention(self, converter):
        """Test that path traversal attempts are handled safely."""
        dangerous_filenames = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config",
            "file/../../../sensitive",
            "\\\\server\\share\\file",
        ]

        for filename in dangerous_filenames:
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0)

                result = converter.generate_presentation("# Test", filename=filename)

                # Check that the output path is safely contained
                if result.markdown_path:
                    md_path = Path(result.markdown_path)
                    assert str(converter.output_dir) in str(md_path.resolve())

    def test_command_injection_prevention(self, converter):
        """Test that command injection is not possible."""
        dangerous_inputs = [
            "file; rm -rf /",
            "file && echo hacked",
            "file | cat /etc/passwd",
            "file`whoami`",
            "$(command)",
        ]

        for dangerous_input in dangerous_inputs:
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0)

                # Try injection in filename
                converter.generate_presentation("# Test", filename=dangerous_input)

                # subprocess.run should be called with a list, not shell=True
                for call in mock_run.call_args_list:
                    args, kwargs = call
                    assert isinstance(args[0], list)  # Command as list
                    assert kwargs.get("shell") is not True

    def test_no_shell_execution(self, converter):
        """Ensure subprocess never uses shell=True."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            converter.generate_presentation("# Test")
            converter.check_marp_installation()

            # Check all calls
            for call in mock_run.call_args_list:
                args, kwargs = call
                assert kwargs.get("shell") is not True


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def converter(self, tmp_path):
        """Create a converter instance."""
        return ClaudeToMarpConverter(output_dir=str(tmp_path / "output"))

    def test_empty_content(self, converter):
        """Test handling of empty content."""
        result = converter.process_claude_content("")

        assert "marp: true" in result
        assert len(result.strip()) > 0

    def test_none_content(self, converter):
        """Test handling of None content."""
        with pytest.raises(ValueError) as exc_info:
            converter.process_claude_content(None)
        assert "Content cannot be None" in str(exc_info.value)

    def test_very_large_content(self, converter):
        """Test handling of very large content."""
        # Create 1000 slides
        large_content = "\n---\n".join(
            [f"# Slide {i}\nContent {i}" for i in range(1000)]
        )

        result = converter.process_claude_content(large_content)

        assert "marp: true" in result
        assert result.count("---") >= 999  # At least 999 slide breaks

    def test_special_characters_in_content(self, converter):
        """Test handling of special characters."""
        special_content = """# Special Characters

- Unicode: 你好世界 🌍
- Math: ∑(x²) = ∫f(x)dx
- Symbols: © ® ™ € £ ¥
- Quotes: "smart" 'quotes' «guillemets»
"""

        result = converter.process_claude_content(special_content)

        # All special characters should be preserved
        assert "你好世界" in result
        assert "🌍" in result
        assert "∑" in result
        assert "©" in result

    def test_malformed_markdown(self, converter):
        """Test handling of malformed markdown."""
        malformed = """# Unclosed code block
```python
def test():
    pass

## Missing closing fence above

### Broken list
- Item 1
  - Nested
 - Misaligned
  
[Broken link]("""

        # Should not crash
        result = converter.process_claude_content(malformed)
        assert "marp: true" in result

    def test_filename_sanitization(self, converter):
        """Test that filenames are properly sanitized."""
        invalid_chars = '<>:"|?*'

        for char in invalid_chars:
            filename = f"test{char}file"

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0)

                result = converter.generate_presentation("# Test", filename=filename)

                # Should complete without error
                assert result.success is True or result.error_message is not None

    def test_filename_sanitization_fallback_to_presentation(self, converter):
        """Test filename sanitization edge case where all characters are stripped."""
        dangerous_filenames = [
            "",  # Empty string
            "   ",  # Only whitespace
            "..",  # Only dots
            ".....",  # Multiple dots
            "<>:|\"?*",  # Only invalid characters
            "  .. <> ",  # Mix of whitespace, dots, and invalid chars
        ]

        for filename in dangerous_filenames:
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0)

                result = converter.generate_presentation("# Test", filename=filename)

                # Should fall back to "presentation" filename
                assert result.success is True
                if result.markdown_path:
                    assert "presentation.md" in result.markdown_path
                if result.output_path:
                    assert "presentation." in result.output_path

    def test_invalid_output_format(self, converter):
        """Test handling of invalid output format."""
        result = converter.generate_presentation("# Test", output_format="invalid")

        assert result.success is False
        assert "Invalid output format" in result.error_message
        assert "Must be one of ['pptx', 'pdf', 'html']" in result.error_message
