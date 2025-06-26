"""
Tool Slide Bridge - Generate PowerPoint compatible slides from AI without friction.

This package provides functionality to convert AI-generated content (specifically
Claude's markdown output) into professional PowerPoint presentations using a hybrid
approach combining MARP for speed and python-pptx for precision.

Main Components:
- MARP Converter: Fast markdown to PowerPoint conversion
- Content Analyzer: Intelligent routing based on content complexity
- Python-PPTX Builder: Advanced PowerPoint generation with precise control
- Hybrid Processor: Combines multiple approaches for optimal results

Usage:
    from tool_slide_bridge import ClaudeToMarpConverter
    
    converter = ClaudeToMarpConverter()
    result = converter.generate_presentation(claude_content, "my_presentation")
"""

__version__ = "0.1.0"
__author__ = "teacherbot"
__email__ = "noreply@github.com"
__license__ = "MIT" 

# Public API imports will be added as modules are implemented
__all__ = [
    "__version__",
    "__author__",
    "__email__", 
    "__license__",
]