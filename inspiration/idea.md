# Claude to PowerPoint Automation Workflow

## Phase 1: MARP Proof of Concept

### Overview
MARP (Markdown Presentation Ecosystem) provides the simplest path from Claude's markdown output to PowerPoint files. This proof of concept demonstrates automated conversion of Claude-generated content into professional presentations.

### Architecture
```
Claude Output (Markdown) → Python Parser → MARP CLI → PowerPoint File
```

### Core Components

#### 1. Markdown Parser (`marp_converter.py`)
```python
import os
import subprocess
import re
from pathlib import Path

class ClaudeToMarpConverter:
    def __init__(self, template_dir="templates", output_dir="presentations"):
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def process_claude_content(self, content, title="presentation"):
        """Convert Claude's markdown/HTML to MARP-compatible markdown"""
        
        # Add MARP directives
        marp_content = self._add_marp_directives(content)
        
        # Clean and structure content
        marp_content = self._structure_slides(marp_content)
        
        # Apply custom styling
        marp_content = self._apply_styling(marp_content)
        
        return marp_content
    
    def _add_marp_directives(self, content):
        """Add MARP front matter and directives"""
        header = """---
marp: true
theme: corporate
class: invert
paginate: true
backgroundColor: #1a1a1a
color: #ffffff
---

"""
        return header + content
    
    def _structure_slides(self, content):
        """Convert content structure to MARP slide breaks"""
        # Replace HTML slide breaks with MARP breaks
        content = re.sub(r'<hr[^>]*>', '\n---\n', content)
        
        # Ensure headings create new slides
        content = re.sub(r'\n(#{1,2}\s)', r'\n---\n\1', content)
        
        # Clean up extra breaks
        content = re.sub(r'\n---\n---\n', '\n---\n', content)
        
        return content
    
    def _apply_styling(self, content):
        """Apply MARP-specific styling directives"""
        # Add slide classes for different content types
        slides = content.split('---')
        styled_slides = []
        
        for slide in slides:
            if re.search(r'#{1}\s', slide):  # Title slide
                slide = '<!-- _class: lead -->\n' + slide
            elif re.search(r'```', slide):  # Code slide
                slide = '<!-- _class: code -->\n' + slide
            
            styled_slides.append(slide)
        
        return '---'.join(styled_slides)
    
    def generate_presentation(self, content, filename="presentation"):
        """Generate PowerPoint from Claude content"""
        
        # Process content
        marp_content = self.process_claude_content(content, filename)
        
        # Save markdown file
        md_file = self.output_dir / f"{filename}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(marp_content)
        
        # Generate PowerPoint using MARP CLI
        pptx_file = self.output_dir / f"{filename}.pptx"
        
        try:
            subprocess.run([
                'marp', str(md_file), 
                '--pptx', 
                '--output', str(pptx_file),
                '--theme', 'corporate'
            ], check=True)
            
            return str(pptx_file)
            
        except subprocess.CalledProcessError as e:
            print(f"MARP conversion failed: {e}")
            return None

# Usage Example
converter = ClaudeToMarpConverter()
claude_output = """
# AI Strategy Presentation

## Overview
This presentation covers our AI implementation strategy.

## Key Benefits
- Increased efficiency
- Cost reduction
- Better insights

## Implementation Timeline
Q1: Planning phase
Q2: Development
Q3: Testing
Q4: Deployment
"""

result = converter.generate_presentation(claude_output, "ai_strategy")
print(f"Presentation generated: {result}")
```

#### 2. Custom MARP Theme (`corporate.css`)
```css
/* Corporate theme for MARP presentations */
@import 'default';

:root {
  --color-primary: #2c5aa0;
  --color-secondary: #34495e;
  --color-accent: #e74c3c;
  --color-background: #ffffff;
  --color-foreground: #2c3e50;
}

section {
  background: var(--color-background);
  color: var(--color-foreground);
  font-family: 'Segoe UI', system-ui, sans-serif;
  font-size: 28px;
  line-height: 1.4;
}

h1 {
  color: var(--color-primary);
  border-bottom: 3px solid var(--color-accent);
  padding-bottom: 0.5em;
}

h2 {
  color: var(--color-secondary);
  margin-top: 1.5em;
}

/* Lead slide (title) styling */
section.lead {
  text-align: center;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  color: white;
}

section.lead h1 {
  font-size: 3em;
  border: none;
  color: white;
}

/* Code slide styling */
section.code {
  background: #1e1e1e;
  color: #d4d4d4;
}

section.code pre {
  background: #2d2d30;
  border-left: 4px solid var(--color-accent);
}
```

### Installation & Setup
```bash
# Install MARP CLI
npm install -g @marp-team/marp-cli

# Install Python dependencies
pip install pathlib

# Set up directory structure
mkdir -p templates presentations themes
```

### Benefits of MARP Approach
- **Speed**: Instant conversion from markdown to PowerPoint
- **Consistency**: Template-based styling ensures brand compliance
- **Simplicity**: Minimal code required for basic functionality
- **Flexibility**: Supports custom themes and advanced styling

### Limitations
- Limited programmatic control over individual elements
- Theme customization requires CSS knowledge
- Complex layouts may need manual adjustment
- Less dynamic content generation capabilities

---

## Phase 2: Hybrid Solution Architecture

### Overview
The hybrid solution combines MARP's speed with python-pptx's precision, offering both rapid prototyping and detailed customization capabilities.

### Enhanced Architecture
```
Claude Output → Content Analyzer → Route Decision → [MARP Path | python-pptx Path] → PowerPoint File
                                                ↓
                                         Post-Processing → Final Output
```

### Core Components

#### 1. Intelligent Content Router (`hybrid_processor.py`)
```python
import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any

class ContentType(Enum):
    SIMPLE_TEXT = "simple_text"
    DATA_HEAVY = "data_heavy"
    INTERACTIVE = "interactive"
    MIXED_MEDIA = "mixed_media"

@dataclass
class SlideRequirement:
    has_charts: bool = False
    has_tables: bool = False
    has_complex_layout: bool = False
    has_animations: bool = False
    word_count: int = 0
    image_count: int = 0

class ContentAnalyzer:
    def __init__(self):
        self.chart_patterns = [
            r'```.*chart.*```',
            r'<chart.*?>',
            r'\|.*\|.*\|',  # Table patterns
            r'data:.*graph'
        ]
        
        self.complex_patterns = [
            r'<div.*class.*>',
            r'style=',
            r'position:',
            r'grid-template'
        ]
    
    def analyze_content(self, content: str) -> ContentType:
        """Analyze Claude's output to determine optimal processing path"""
        
        requirements = self._extract_requirements(content)
        
        # Decision logic
        if requirements.has_charts or requirements.has_tables:
            return ContentType.DATA_HEAVY
            
        if requirements.has_complex_layout or requirements.has_animations:
            return ContentType.INTERACTIVE
            
        if requirements.image_count > 3 or requirements.word_count > 500:
            return ContentType.MIXED_MEDIA
            
        return ContentType.SIMPLE_TEXT
    
    def _extract_requirements(self, content: str) -> SlideRequirement:
        """Extract detailed requirements from content"""
        
        req = SlideRequirement()
        
        # Check for charts/data
        req.has_charts = any(re.search(pattern, content, re.IGNORECASE) 
                           for pattern in self.chart_patterns)
        
        # Check for complex layouts
        req.has_complex_layout = any(re.search(pattern, content, re.IGNORECASE) 
                                   for pattern in self.complex_patterns)
        
        # Count elements
        req.word_count = len(content.split())
        req.image_count = len(re.findall(r'!\[.*?\]', content))
        
        # Check for tables
        req.has_tables = '|' in content and content.count('|') > 4
        
        return req

class HybridProcessor:
    def __init__(self):
        self.analyzer = ContentAnalyzer()
        self.marp_converter = ClaudeToMarpConverter()
        self.pptx_builder = PythonPptxBuilder()
    
    def process_content(self, content: str, filename: str = "presentation") -> str:
        """Route content through optimal processing path"""
        
        content_type = self.analyzer.analyze_content(content)
        
        if content_type == ContentType.SIMPLE_TEXT:
            # Fast path: Use MARP
            return self.marp_converter.generate_presentation(content, filename)
            
        elif content_type in [ContentType.DATA_HEAVY, ContentType.INTERACTIVE]:
            # Precision path: Use python-pptx
            return self.pptx_builder.generate_presentation(content, filename)
            
        else:  # MIXED_MEDIA
            # Hybrid path: MARP + python-pptx post-processing
            return self._hybrid_generation(content, filename)
    
    def _hybrid_generation(self, content: str, filename: str) -> str:
        """Generate using MARP then enhance with python-pptx"""
        
        # Generate base presentation with MARP
        base_file = self.marp_converter.generate_presentation(content, f"{filename}_base")
        
        # Enhance with python-pptx
        enhanced_file = self.pptx_builder.enhance_presentation(base_file, content, filename)
        
        return enhanced_file
```

#### 2. Advanced python-pptx Builder (`pptx_builder.py`)
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import re
import json

class PythonPptxBuilder:
    def __init__(self, template_path=None):
        self.template_path = template_path
        self.corporate_colors = {
            'primary': RGBColor(44, 90, 160),
            'secondary': RGBColor(52, 73, 94),
            'accent': RGBColor(231, 76, 60),
            'text': RGBColor(44, 62, 80)
        }
    
    def generate_presentation(self, content: str, filename: str) -> str:
        """Generate presentation with full python-pptx control"""
        
        if self.template_path:
            prs = Presentation(self.template_path)
        else:
            prs = Presentation()
        
        # Parse content into slides
        slides_data = self._parse_content_structure(content)
        
        # Generate slides
        for slide_data in slides_data:
            self._create_slide(prs, slide_data)
        
        # Save presentation
        output_path = f"presentations/{filename}.pptx"
        prs.save(output_path)
        
        return output_path
    
    def _parse_content_structure(self, content: str) -> List[Dict]:
        """Parse Claude content into structured slide data"""
        
        slides = []
        current_slide = {'type': 'content', 'title': '', 'content': [], 'charts': [], 'tables': []}
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('# '):
                # New title slide
                if current_slide['title'] or current_slide['content']:
                    slides.append(current_slide)
                current_slide = {'type': 'title', 'title': line[2:], 'content': [], 'charts': [], 'tables': []}
                
            elif line.startswith('## '):
                # New content slide
                if current_slide['title'] or current_slide['content']:
                    slides.append(current_slide)
                current_slide = {'type': 'content', 'title': line[3:], 'content': [], 'charts': [], 'tables': []}
                
            elif line.startswith('```') and 'chart' in line.lower():
                # Chart data
                current_slide['charts'].append(self._extract_chart_data(line))
                
            elif '|' in line and line.count('|') > 2:
                # Table row
                current_slide['tables'].append(line.split('|'))
                
            elif line:
                # Regular content
                current_slide['content'].append(line)
        
        if current_slide['title'] or current_slide['content']:
            slides.append(current_slide)
        
        return slides
    
    def _create_slide(self, prs: Presentation, slide_data: Dict):
        """Create a slide based on structured data"""
        
        if slide_data['type'] == 'title':
            slide_layout = prs.slide_layouts[0]  # Title slide layout
            slide = prs.slides.add_slide(slide_layout)
            
            title = slide.shapes.title
            title.text = slide_data['title']
            title.text_frame.paragraphs[0].font.color.rgb = self.corporate_colors['primary']
            
        else:
            slide_layout = prs.slide_layouts[1]  # Content slide layout
            slide = prs.slides.add_slide(slide_layout)
            
            # Set title
            title = slide.shapes.title
            title.text = slide_data['title']
            
            # Add content
            if slide_data['content']:
                self._add_content_to_slide(slide, slide_data['content'])
            
            # Add charts
            if slide_data['charts']:
                self._add_charts_to_slide(slide, slide_data['charts'])
            
            # Add tables
            if slide_data['tables']:
                self._add_tables_to_slide(slide, slide_data['tables'])
    
    def _add_content_to_slide(self, slide, content_lines: List[str]):
        """Add text content to slide with proper formatting"""
        
        content_placeholder = slide.placeholders[1]
        text_frame = content_placeholder.text_frame
        text_frame.clear()
        
        for i, line in enumerate(content_lines):
            if i == 0:
                p = text_frame.paragraphs[0]
            else:
                p = text_frame.add_paragraph()
            
            p.text = line
            p.font.size = Pt(18)
            p.font.color.rgb = self.corporate_colors['text']
            
            if line.startswith('- ') or line.startswith('• '):
                p.level = 1
                p.text = line[2:]  # Remove bullet marker
    
    def _add_charts_to_slide(self, slide, chart_data: List):
        """Add charts to slide"""
        # Implementation for chart generation
        # This would integrate with libraries like matplotlib or plotly
        pass
    
    def _add_tables_to_slide(self, slide, table_data: List):
        """Add tables to slide"""
        if not table_data:
            return
        
        # Create table
        rows = len(table_data)
        cols = len(table_data[0]) if table_data else 1
        
        left = Inches(1)
        top = Inches(3)
        width = Inches(8)
        height = Inches(3)
        
        table = slide.shapes.add_table(rows, cols, left, top, width, height).table
        
        # Populate table
        for i, row_data in enumerate(table_data):
            for j, cell_data in enumerate(row_data):
                if j < cols:  # Ensure we don't exceed column count
                    cell = table.cell(i, j)
                    cell.text = str(cell_data).strip()
                    
                    # Header row styling
                    if i == 0:
                        cell.fill.solid()
                        cell.fill.fore_color.rgb = self.corporate_colors['primary']
                        for paragraph in cell.text_frame.paragraphs:
                            paragraph.font.color.rgb = RGBColor(255, 255, 255)
                            paragraph.font.bold = True
    
    def enhance_presentation(self, base_file: str, content: str, filename: str) -> str:
        """Enhance MARP-generated presentation with python-pptx"""
        
        # Load existing presentation
        prs = Presentation(base_file)
        
        # Apply enhancements
        self._apply_corporate_branding(prs)
        self._add_dynamic_content(prs, content)
        
        # Save enhanced version
        output_path = f"presentations/{filename}_enhanced.pptx"
        prs.save(output_path)
        
        return output_path
    
    def _apply_corporate_branding(self, prs: Presentation):
        """Apply consistent corporate branding"""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, 'text_frame'):
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            if run.font.size and run.font.size > Pt(24):
                                run.font.color.rgb = self.corporate_colors['primary']
    
    def _extract_chart_data(self, chart_line: str) -> Dict:
        """Extract chart data from Claude's chart notation"""
        # Parse chart specifications
        # This would handle various chart types and data formats
        return {'type': 'bar', 'data': []}
```

#### 3. CLI Interface (`claude_pptx_cli.py`)
```python
import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Convert Claude content to PowerPoint')
    parser.add_argument('input_file', help='Input markdown/HTML file from Claude')
    parser.add_argument('-o', '--output', default='presentation', help='Output filename')
    parser.add_argument('-m', '--mode', choices=['marp', 'pptx', 'hybrid'], default='hybrid',
                       help='Processing mode')
    parser.add_argument('-t', '--template', help='PowerPoint template file')
    parser.add_argument('--theme', default='corporate', help='MARP theme name')
    
    args = parser.parse_args()
    
    # Read input content
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    # Process based on mode
    if args.mode == 'marp':
        converter = ClaudeToMarpConverter()
        result = converter.generate_presentation(content, args.output)
    elif args.mode == 'pptx':
        builder = PythonPptxBuilder(args.template)
        result = builder.generate_presentation(content, args.output)
    else:  # hybrid
        processor = HybridProcessor()
        result = processor.process_content(content, args.output)
    
    if result:
        print(f"✅ Presentation generated: {result}")
    else:
        print("❌ Failed to generate presentation")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Usage Examples

#### Basic MARP Conversion
```bash
python claude_pptx_cli.py claude_output.md -o "quarterly_review" -m marp
```

#### Advanced python-pptx Generation
```bash
python claude_pptx_cli.py claude_data_heavy.md -o "analytics_report" -m pptx -t corporate_template.pptx
```

#### Intelligent Hybrid Processing
```bash
python claude_pptx_cli.py claude_mixed.md -o "strategy_deck" -m hybrid
```

### Benefits of Hybrid Approach
- **Intelligent Routing**: Automatically selects optimal processing method
- **Speed + Precision**: Fast generation for simple content, detailed control for complex presentations
- **Template Support**: Corporate branding and consistent styling
- **Extensible**: Easy to add new content types and processing methods
- **CLI Integration**: Simple command-line interface for automation

### Future Enhancements
1. **AI Content Analysis**: Use NLP to better understand content structure
2. **Dynamic Chart Generation**: Automatic chart creation from data
3. **Template Learning**: AI-powered template suggestions
4. **Real-time Collaboration**: Integration with cloud presentation platforms
5. **Multi-format Output**: Support for additional presentation formats

This hybrid solution provides the foundation for a robust, automated presentation generation system that scales from simple markdown conversions to complex, data-driven presentations.

---

## Phase 3: Live Interactive Web Converter

### Overview
A browser-based interactive artifact that allows users to paste Claude-generated markdown, preview slides in real-time, and instantly download PowerPoint files. This approach requires no local installation and works entirely in the browser.

### Architecture
```
User Input (Markdown) → React Interface → Claude Enhancement (Optional) → PptxGenJS → Download PPTX
                                    ↓
                              Live Preview → User Adjustments
```

### Technical Implementation
- **Frontend**: React artifact with real-time preview
- **Processing**: JavaScript-based markdown parsing
- **Generation**: PptxGenJS library for PPTX creation
- **Enhancement**: Optional Claude API calls for content improvement
- **Download**: Browser-native file download

### Key Features
1. **Live Preview**: See slides as you type
2. **Claude Enhancement**: AI-powered content suggestions
3. **Template Selection**: Choose from multiple corporate themes
4. **Instant Download**: Generate and download PPTX immediately
5. **No Installation**: Works entirely in browser
6. **Responsive Design**: Works on desktop and mobile

### Benefits
- **Zero Setup**: No CLI tools or Python installation required
- **Immediate Feedback**: Live preview and instant results
- **User Friendly**: Simple drag-and-drop or paste interface
- **Collaborative**: Easy to share and use across teams
- **Portable**: Works anywhere with a web browser

### Limitations
- **JavaScript Only**: Limited to browser-compatible libraries
- **File Size**: Large presentations may hit browser memory limits
- **Advanced Features**: Complex animations/transitions may be limited
- **Offline**: Requires internet for Claude API enhancement features

This live converter represents the most accessible approach, perfect for quick conversions and team collaboration.
