# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project aims to create a tool that converts AI-generated content (specifically Claude's markdown output) into PowerPoint presentations without friction. The goal is to bridge the gap between AI content generation and professional presentation formats.

## Project Status

This is a **greenfield project** in the planning phase. The codebase currently contains only:
- Basic README with project description
- Detailed implementation plan in `inspiration/idea.md`
- MIT license

## Architecture Plan

The project is designed around a **3-phase approach**:

1. **Phase 1: MARP Proof of Concept** - Simple markdown to PowerPoint conversion using MARP CLI
2. **Phase 2: Hybrid Solution** - Intelligent routing between MARP (for speed) and python-pptx (for precision)
3. **Phase 3: Live Interactive Web Converter** - Browser-based React interface with real-time preview

## Key Technical Components (Planned)

### Core Technologies
- **MARP CLI**: Fast markdown to PowerPoint conversion
- **python-pptx**: Precise PowerPoint generation and manipulation
- **PptxGenJS**: Browser-based PowerPoint generation
- **React**: Interactive web interface

### Architecture Patterns
- **Intelligent Content Routing**: Automatically select optimal processing method based on content complexity
- **Hybrid Processing**: Combine MARP speed with python-pptx precision
- **Template System**: Corporate branding and consistent styling

## Development Setup

Since this is a new project, the development environment will need to be established:

### Dependencies (When Implemented)
- Node.js and npm (for MARP CLI)
- Python 3.x (for python-pptx processing)
- React development environment (for web interface)

### Key Commands (To Be Implemented)
```bash
# Install MARP CLI
npm install -g @marp-team/marp-cli

# Python dependencies
pip install python-pptx pathlib

# CLI usage (planned)
python claude_pptx_cli.py input.md -o presentation -m hybrid
```

## File Structure (Planned)

```
├── src/
│   ├── marp_converter.py      # MARP-based conversion
│   ├── pptx_builder.py        # python-pptx advanced generation
│   ├── hybrid_processor.py    # Intelligent content routing
│   └── claude_pptx_cli.py     # CLI interface
├── templates/                 # PowerPoint templates
├── themes/                    # MARP themes (CSS)
├── presentations/             # Generated output
└── web/                       # React web interface
```

## Content Processing Strategy

The system will analyze Claude's markdown output to determine the optimal processing path:
- **Simple text content** → Fast MARP conversion
- **Data-heavy content** (charts, tables) → Precise python-pptx generation
- **Mixed media** → Hybrid approach with post-processing

## Implementation Priority

1. Start with Phase 1 (MARP proof of concept) for rapid prototyping
2. Implement content analysis and routing logic
3. Build python-pptx integration for complex content
4. Develop web interface for user-friendly interaction

## Notes

- The project emphasizes automation and minimal user friction
- Corporate branding and template consistency are key requirements
- The hybrid approach balances speed with precision based on content complexity