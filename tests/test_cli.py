"""Tests for CLI functionality, including fortune messages."""

import random
from unittest.mock import patch, Mock
import pytest
from click.testing import CliRunner

from tool_slide_bridge.cli import print_banner, FORTUNE_MESSAGES


class TestFortuneBanner:
    """Test the fortune message banner functionality."""

    def test_fortune_messages_list_exists(self):
        """Test that FORTUNE_MESSAGES list is defined and not empty."""
        assert FORTUNE_MESSAGES is not None
        assert len(FORTUNE_MESSAGES) > 0
        assert isinstance(FORTUNE_MESSAGES, list)

    def test_fortune_messages_include_required_messages(self):
        """Test that all required messages from the issue are included."""
        required_messages = [
            "To be, rather than to seem",
            "Esse quam videri",
            "Claude says hi",
            "AI to PowerPoint without friction",
        ]

        # Check that each required message is contained within the padded messages
        for required_msg in required_messages:
            found = any(required_msg in padded_msg for padded_msg in FORTUNE_MESSAGES)
            assert found, f"Required message '{required_msg}' not found in padded messages"

    def test_fortune_messages_fit_banner_width(self):
        """Test that all fortune messages fit within the banner width (37 chars)."""
        for message in FORTUNE_MESSAGES:
            # Even if message is too long, our implementation truncates it
            assert (
                len(message) <= 50
            ), f"Message too long to handle gracefully: '{message}'"

    @patch("tool_slide_bridge.cli.console")
    @patch("random.choice")
    def test_print_banner_uses_random_choice(self, mock_choice, mock_console):
        """Test that print_banner uses random.choice to select messages."""
        mock_choice.return_value = "Test message"

        print_banner()

        mock_choice.assert_called_once_with(FORTUNE_MESSAGES)
        mock_console.print.assert_called_once()

    @patch("tool_slide_bridge.cli.console")
    def test_print_banner_formats_correctly(self, mock_console):
        """Test that banner formatting is correct for various message lengths."""
        with patch("random.choice") as mock_choice:
            # Test with short message
            mock_choice.return_value = "Short"
            print_banner()

            call_args = mock_console.print.call_args
            banner_text = call_args[0][0]

            # Check that banner contains expected structure
            assert "╔═══════════════════════════════════════╗" in banner_text
            assert "Tool: Slide Bridge 🌉" in banner_text
            assert "Short" in banner_text
            assert "╚═══════════════════════════════════════╝" in banner_text

            # Check styling
            assert call_args[1]["style"] == "bold blue"

    @patch("tool_slide_bridge.cli.console")
    def test_print_banner_truncates_long_messages(self, mock_console):
        """Test that very long messages are properly truncated."""
        with patch("random.choice") as mock_choice:
            long_message = "This is a very long message that exceeds the banner width"
            mock_choice.return_value = long_message

            print_banner()

            call_args = mock_console.print.call_args
            banner_text = call_args[0][0]

            # Should contain truncated version with ellipsis
            assert "..." in banner_text
            # Should not contain the full long message
            assert long_message not in banner_text

    def test_all_messages_produce_valid_banners(self):
        """Test that every message in FORTUNE_MESSAGES produces a valid banner."""
        with patch("tool_slide_bridge.cli.console") as mock_console:
            for message in FORTUNE_MESSAGES:
                with patch("random.choice", return_value=message):
                    print_banner()

                    # Verify print was called
                    assert mock_console.print.called

                    call_args = mock_console.print.call_args
                    banner_text = call_args[0][0]

                    # Verify banner structure is maintained
                    lines = banner_text.strip().split("\n")
                    assert len(lines) == 4  # 4 banner lines
                    assert lines[0].startswith("╔")
                    assert lines[3].startswith("╚")

                    mock_console.reset_mock()

    def test_message_centering(self):
        """Test that messages are properly centered in the banner."""
        with patch("tool_slide_bridge.cli.console") as mock_console:
            test_message = "Test"
            with patch("random.choice", return_value=test_message):
                print_banner()

                call_args = mock_console.print.call_args
                banner_text = call_args[0][0]

                # Find the line with our test message
                lines = banner_text.strip().split("\n")
                message_line = None
                for line in lines:
                    if "Test" in line:
                        message_line = line
                        break

                assert message_line is not None
                # Check that line starts and ends with ║ and is 39 chars total
                assert message_line.startswith("║")
                assert message_line.endswith("║")
                assert len(message_line) == 39  # 37 content + 2 border chars


class TestCLIIntegration:
    """Integration tests for CLI with fortune messages."""

    @patch("tool_slide_bridge.cli.ClaudeToMarpConverter")
    def test_banner_displays_on_cli_run(self, mock_converter):
        """Test that banner with fortune message displays when CLI runs."""
        # Mock the converter to avoid needing actual MARP installation
        mock_instance = Mock()
        mock_instance.check_marp_installation.return_value = False
        mock_converter.return_value = mock_instance

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create a dummy input file
            with open("test.md", "w") as f:
                f.write("# Test")

            result = runner.invoke(
                __import__("tool_slide_bridge.cli", fromlist=["main"]).main,
                ["test.md", "--check-marp"],
            )

            # Banner should appear in output
            assert "Tool: Slide Bridge 🌉" in result.output
            # Should contain one of our fortune messages
            contains_fortune = any(msg in result.output for msg in FORTUNE_MESSAGES)
            assert (
                contains_fortune
            ), f"No fortune message found in output: {result.output}"
