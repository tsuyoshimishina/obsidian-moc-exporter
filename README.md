# obsidian-moc-exporter

A CLI tool that recursively traverses links from a specified Obsidian MOC (Map of Content) note and exports all referenced notes and attachments in standard Markdown format, suitable for importing into NotebookLM.

## Features

- Recursively follows wiki-links from a MOC file
- Converts Obsidian-flavored Markdown to standard Markdown
- Exports all referenced notes and attachments
- Flat output structure (compatible with NotebookLM)
- Configurable traversal depth

## Installation

### Requirements

- Python 3.11+
- No external dependencies (uses standard library only)

### Setup

```bash
# Create conda environment
conda create -n obsidian-moc-exporter python=3.11 -y
conda activate obsidian-moc-exporter

# Clone or download the repository
cd obsidian-moc-exporter
```

## Usage

```bash
python main.py --vault "path/to/vault" --moc "MOC.md" --output "path/to/output" [--depth 2]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--vault` | Yes | Path to Obsidian vault root directory |
| `--moc` | Yes | Path to MOC file (relative to vault or filename) |
| `--output` | Yes | Output directory path |
| `--depth` | No | Maximum link traversal depth (default: 2) |

### Example

```bash
python main.py --vault "C:/Users/username/ObsidianVault" --moc "Projects/MOC-ProjectX.md" --output "C:/export" --depth 2
```

## Conversion Rules

| Obsidian Syntax | Standard Markdown |
|-----------------|-------------------|
| `[[Page]]` | `[Page](Page.md)` |
| `[[Page\|Alias]]` | `[Alias](Page.md)` |
| `![[Note]]` (embed) | `[Note](Note.md)` |
| `![[image.png]]` | `![image](image.png)` |
| `![[image.png\|alt]]` | `![alt](image.png)` |
| `![[image.png\|alt\|300]]` | `![alt](image.png)` |
| `![[image.png\|300]]` | `![image](image.png)` |
| `%%comment%%` | (removed) |
| `#tag` | (preserved) |
| Frontmatter | (preserved) |

## Output Structure

All files are placed flat in the output directory (no subfolders):

```
output/
├── MOC.md
├── LinkedNote1.md
├── LinkedNote2.md
├── image.png
└── document.pdf
```

## Supported Attachments

- **Images:** `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.bmp`
- **Documents:** `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`
- **Media:** `.mp3`, `.wav`, `.mp4`, `.webm`, `.ogg`

## License

TBD
