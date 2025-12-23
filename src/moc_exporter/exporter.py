"""Main export logic for Obsidian MOC Exporter."""

import re
import shutil
from pathlib import Path
from typing import List, Tuple


class ObsidianMOCExporter:
    """Export Obsidian notes starting from a MOC file to standard Markdown."""

    # Regex patterns for Obsidian syntax
    WIKILINK_PATTERN = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
    EMBED_PATTERN = re.compile(r'!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
    COMMENT_PATTERN = re.compile(r'%%.*?%%', re.DOTALL)

    # Supported attachment extensions
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp'}
    DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'}
    MEDIA_EXTENSIONS = {'.mp3', '.wav', '.mp4', '.webm', '.ogg'}
    ATTACHMENT_EXTENSIONS = IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS | MEDIA_EXTENSIONS

    def __init__(self, vault_path: Path, output_path: Path, max_depth: int = 2):
        """
        Initialize the exporter.

        Args:
            vault_path: Path to the Obsidian vault root
            output_path: Path to the output directory
            max_depth: Maximum link traversal depth (default: 2)
        """
        self.vault_path = vault_path
        self.output_path = output_path
        self.max_depth = max_depth
        self.collected_notes: dict[Path, int] = {}  # note_path -> depth
        self.collected_attachments: set[Path] = set()
        self._note_cache: dict[str, Path] = {}  # filename -> full path

    def _build_note_cache(self) -> None:
        """Build a cache of all markdown files in the vault for fast lookup."""
        for md_file in self.vault_path.rglob('*.md'):
            # Store by filename (without extension) for wiki-link lookup
            name = md_file.stem
            if name not in self._note_cache:
                self._note_cache[name] = md_file

    def find_note_file(self, link_target: str) -> Path | None:
        """
        Find the actual file path for a wiki-link target.

        Args:
            link_target: The target of a wiki-link (e.g., "Note Name" or "folder/Note")

        Returns:
            Path to the note file if found, None otherwise
        """
        # Build cache on first call
        if not self._note_cache:
            self._build_note_cache()

        # Remove any heading or block reference
        link_target = link_target.split('#')[0].strip()
        if not link_target:
            return None

        # Try as direct path first
        direct_path = self.vault_path / link_target
        if not direct_path.suffix:
            direct_path = direct_path.with_suffix('.md')
        if direct_path.exists():
            return direct_path

        # Try finding by filename in cache
        name = Path(link_target).stem
        if name in self._note_cache:
            return self._note_cache[name]

        return None

    def find_attachment_file(self, link_target: str) -> Path | None:
        """
        Find the actual file path for an attachment link.

        Args:
            link_target: The target of an attachment link (e.g., "image.png")

        Returns:
            Path to the attachment file if found, None otherwise
        """
        # Try as direct path first
        direct_path = self.vault_path / link_target
        if direct_path.exists():
            return direct_path

        # Search in common attachment directories
        for search_dir in ['attachments', 'assets', 'images', 'files', '']:
            search_path = self.vault_path / search_dir if search_dir else self.vault_path
            if search_path.exists():
                for attachment in search_path.rglob(Path(link_target).name):
                    return attachment

        return None

    def is_attachment(self, filename: str) -> bool:
        """
        Check if a filename is an attachment based on its extension.

        Args:
            filename: The filename to check

        Returns:
            True if the file is an attachment, False otherwise
        """
        ext = Path(filename).suffix.lower()
        return ext in self.ATTACHMENT_EXTENSIONS

    def is_image(self, filename: str) -> bool:
        """
        Check if a filename is an image based on its extension.

        Args:
            filename: The filename to check

        Returns:
            True if the file is an image, False otherwise
        """
        ext = Path(filename).suffix.lower()
        return ext in self.IMAGE_EXTENSIONS

    def extract_links(self, content: str) -> List[Tuple[str, str | None, bool]]:
        """
        Extract all wiki-links and embeds from content.

        Args:
            content: The markdown content to parse

        Returns:
            List of tuples (target, alias, is_embed)
        """
        links = []

        # Extract embeds first
        for match in self.EMBED_PATTERN.finditer(content):
            target = match.group(1)
            alias = match.group(2)
            links.append((target, alias, True))

        # Extract regular wiki-links
        for match in self.WIKILINK_PATTERN.finditer(content):
            target = match.group(1)
            alias = match.group(2)
            links.append((target, alias, False))

        return links

    def convert_to_standard_markdown(self, content: str) -> str:
        """
        Convert Obsidian-flavored markdown to standard markdown.

        Args:
            content: The Obsidian markdown content

        Returns:
            Standard markdown content
        """
        # Remove comments
        content = self.COMMENT_PATTERN.sub('', content)

        # Convert embeds to links/images
        def replace_embed(match: re.Match) -> str:
            target = match.group(1)
            alias = match.group(2)

            # Remove heading/block references for filename
            filename = target.split('#')[0]

            if self.is_attachment(filename):
                # Find and collect the attachment
                attachment_path = self.find_attachment_file(filename)
                if attachment_path:
                    self.collected_attachments.add(attachment_path)

                # Use just the filename for flat output structure
                output_filename = Path(filename).name

                if self.is_image(filename):
                    # Image: ![alt](image.png)
                    alt_text = alias if alias else Path(filename).stem
                    return f'![{alt_text}]({output_filename})'
                else:
                    # Other attachment: [name](file.pdf)
                    link_text = alias if alias else Path(filename).name
                    return f'[{link_text}]({output_filename})'
            else:
                # Note embed -> regular link
                link_text = alias if alias else target
                note_filename = Path(filename).stem + '.md'
                return f'[{link_text}]({note_filename})'

        content = self.EMBED_PATTERN.sub(replace_embed, content)

        # Convert wiki-links
        def replace_wikilink(match: re.Match) -> str:
            target = match.group(1)
            alias = match.group(2)

            # Handle heading/block references
            filename = target.split('#')[0]
            link_text = alias if alias else target

            if self.is_attachment(filename):
                # Attachment link
                attachment_path = self.find_attachment_file(filename)
                if attachment_path:
                    self.collected_attachments.add(attachment_path)
                output_filename = Path(filename).name
                return f'[{link_text}]({output_filename})'
            else:
                # Note link
                note_filename = (Path(filename).stem + '.md') if filename else target
                return f'[{link_text}]({note_filename})'

        content = self.WIKILINK_PATTERN.sub(replace_wikilink, content)

        return content

    def collect_notes_recursive(self, note_path: Path, current_depth: int = 0) -> None:
        """
        Recursively collect notes starting from a given note.

        Args:
            note_path: Path to the starting note
            current_depth: Current traversal depth
        """
        # Skip if already collected at same or lower depth
        if note_path in self.collected_notes:
            if self.collected_notes[note_path] <= current_depth:
                return

        self.collected_notes[note_path] = current_depth

        # Stop recursion if max depth reached
        if current_depth >= self.max_depth:
            return

        # Read and parse the note
        try:
            content = note_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read {note_path}: {e}")
            return

        # Extract links and process them
        links = self.extract_links(content)
        for target, _, is_embed in links:
            # Remove heading/block references
            filename = target.split('#')[0].strip()
            if not filename:
                continue

            if self.is_attachment(filename):
                # Collect attachment
                attachment_path = self.find_attachment_file(filename)
                if attachment_path:
                    self.collected_attachments.add(attachment_path)
            else:
                # Recursively collect linked note
                linked_note = self.find_note_file(filename)
                if linked_note:
                    self.collect_notes_recursive(linked_note, current_depth + 1)

    def export(self, moc_path: str) -> dict:
        """
        Export notes starting from a MOC file.

        Args:
            moc_path: Path to the MOC file, relative to vault or filename

        Returns:
            Dictionary with export statistics
        """
        # Find the MOC file
        moc_file = self.find_note_file(moc_path)
        if not moc_file:
            # Try as direct path
            moc_file = self.vault_path / moc_path
            if not moc_file.exists():
                raise FileNotFoundError(f"MOC file not found: {moc_path}")

        print(f"Starting export from: {moc_file}")
        print(f"Max depth: {self.max_depth}")

        # Collect all notes recursively
        self.collect_notes_recursive(moc_file, current_depth=0)

        print(f"Collected {len(self.collected_notes)} notes")
        print(f"Collected {len(self.collected_attachments)} attachments")

        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Export notes
        exported_notes = 0
        for note_path in self.collected_notes:
            try:
                content = note_path.read_text(encoding='utf-8')
                converted = self.convert_to_standard_markdown(content)

                # Write to output (flat structure)
                output_file = self.output_path / note_path.name

                # Handle filename collisions
                if output_file.exists():
                    stem = output_file.stem
                    suffix = output_file.suffix
                    counter = 1
                    while output_file.exists():
                        output_file = self.output_path / f"{stem}_{counter}{suffix}"
                        counter += 1

                output_file.write_text(converted, encoding='utf-8')
                exported_notes += 1
            except Exception as e:
                print(f"Warning: Could not export {note_path}: {e}")

        # Copy attachments
        exported_attachments = 0
        for attachment_path in self.collected_attachments:
            try:
                output_file = self.output_path / attachment_path.name

                # Handle filename collisions
                if output_file.exists():
                    stem = output_file.stem
                    suffix = output_file.suffix
                    counter = 1
                    while output_file.exists():
                        output_file = self.output_path / f"{stem}_{counter}{suffix}"
                        counter += 1

                shutil.copy2(attachment_path, output_file)
                exported_attachments += 1
            except Exception as e:
                print(f"Warning: Could not copy {attachment_path}: {e}")

        stats = {
            'notes_collected': len(self.collected_notes),
            'notes_exported': exported_notes,
            'attachments_collected': len(self.collected_attachments),
            'attachments_exported': exported_attachments,
        }

        print(f"\nExport complete!")
        print(f"Notes exported: {exported_notes}")
        print(f"Attachments exported: {exported_attachments}")
        print(f"Output directory: {self.output_path}")

        return stats
