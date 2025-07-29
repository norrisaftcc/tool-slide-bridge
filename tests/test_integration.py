"""Integration tests that verify end-to-end functionality."""

from pathlib import Path

import pytest

from tool_slide_bridge import ClaudeToMarpConverter, MarpConfig


class TestIntegration:
    """Integration tests for the complete workflow."""

    @pytest.fixture
    def sample_presentation(self):
        """Sample presentation content that Claude might generate."""
        return """# Machine Learning Fundamentals

An introduction to key concepts and techniques

---

## What is Machine Learning?

Machine Learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.

### Key Components:
- **Data**: The foundation of all ML systems
- **Algorithms**: Methods for learning patterns
- **Models**: Mathematical representations of patterns

---

## Types of Machine Learning

### 1. Supervised Learning
- Uses labeled training data
- Examples: Classification, Regression

### 2. Unsupervised Learning  
- Finds patterns in unlabeled data
- Examples: Clustering, Dimensionality Reduction

### 3. Reinforcement Learning
- Learns through trial and error
- Examples: Game AI, Robotics

---

## Common Algorithms

```python
# Example: Simple Linear Regression
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

---

## Best Practices

1. **Data Quality**: Garbage in, garbage out
2. **Feature Engineering**: Transform raw data effectively  
3. **Model Validation**: Always use cross-validation
4. **Avoid Overfitting**: Keep models generalizable

---

## Thank You!

Questions?

Contact: ml-team@example.com"""

    def test_full_workflow_markdown_generation(self, tmp_path, sample_presentation):
        """Test the complete workflow from Claude content to markdown file."""
        # Create converter with temp directory
        converter = ClaudeToMarpConverter(output_dir=str(tmp_path / "output"))

        # Process the content
        config = MarpConfig(theme="corporate", paginate=True, enable_html=True)

        marp_content = converter.process_claude_content(
            sample_presentation, config=config
        )

        # Verify MARP directives
        assert "marp: true" in marp_content
        assert "paginate: true" in marp_content
        assert "html: true" in marp_content

        # Verify content structure
        assert "# Machine Learning Fundamentals" in marp_content
        assert "```python" in marp_content
        assert "Contact: ml-team@example.com" in marp_content

        # Verify slide breaks
        slide_count = marp_content.count("\n---\n")
        assert slide_count >= 5  # Should have at least 5 slide breaks

        # Verify styling
        assert "<!-- _class:" in marp_content  # Should have styling directives

    def test_file_creation_and_paths(self, tmp_path, sample_presentation):
        """Test that files are created in the correct locations."""
        output_dir = tmp_path / "presentations"
        converter = ClaudeToMarpConverter(output_dir=str(output_dir))

        # Generate presentation (mocked subprocess)
        from unittest.mock import Mock, patch

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            result = converter.generate_presentation(
                sample_presentation, filename="test_presentation"
            )

            # Verify result
            assert result.success is True
            assert result.markdown_path is not None
            assert result.output_path is not None

            # Verify markdown file was created
            md_path = Path(result.markdown_path)
            assert md_path.exists()
            assert md_path.name == "test_presentation.md"

            # Verify content
            content = md_path.read_text()
            assert "marp: true" in content
            assert "Machine Learning Fundamentals" in content

    def test_security_validation_integration(self, tmp_path):
        """Test security features in real workflow."""
        converter = ClaudeToMarpConverter(output_dir=str(tmp_path))

        # Try dangerous filename
        dangerous_filename = "../../../etc/passwd"

        from unittest.mock import Mock, patch

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            result = converter.generate_presentation(
                "# Test", filename=dangerous_filename
            )

            # Should sanitize the filename
            if result.markdown_path:
                path = Path(result.markdown_path)
                # Should not escape the output directory
                assert str(tmp_path) in str(path.resolve())
                # Should not contain path traversal
                assert ".." not in path.name

    def test_error_handling_integration(self, tmp_path):
        """Test error handling in real scenarios."""
        converter = ClaudeToMarpConverter(output_dir=str(tmp_path))

        # Test with None content in process_claude_content
        with pytest.raises(ValueError):
            converter.process_claude_content(None)

        # Test with invalid format
        result = converter.generate_presentation(
            "# Test", output_format="docx"  # Not supported
        )
        assert result.success is False
        assert "Invalid output format" in result.error_message
