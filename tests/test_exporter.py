"""Unit tests for ObsidianMOCExporter."""

import pytest
import tempfile
from pathlib import Path

from src.moc_exporter.exporter import ObsidianMOCExporter


class TestConvertToStandardMarkdown:
    """Tests for convert_to_standard_markdown method."""

    @pytest.fixture
    def exporter(self, tmp_path):
        """Create an exporter instance with a temporary vault."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        output_path = tmp_path / "output"
        return ObsidianMOCExporter(vault_path, output_path)

    # Image embed tests
    def test_image_embed_basic(self, exporter):
        """Test basic image embed without alias."""
        content = "![[image.png]]"
        result = exporter.convert_to_standard_markdown(content)
        assert result == "![image](image.png)"

    def test_image_embed_with_alt_text(self, exporter):
        """Test image embed with alt text."""
        content = "![[image.png|description]]"
        result = exporter.convert_to_standard_markdown(content)
        assert result == "![description](image.png)"

    def test_image_embed_with_width_only(self, exporter):
        """Test image embed with width specification only."""
        content = "![[image.png|300]]"
        result = exporter.convert_to_standard_markdown(content)
        assert result == "![image](image.png)"

    def test_image_embed_with_alt_and_width(self, exporter):
        """Test image embed with alt text and width specification."""
        content = "![[image.png|description|300]]"
        result = exporter.convert_to_standard_markdown(content)
        assert result == "![description](image.png)"

    def test_image_embed_with_dimensions(self, exporter):
        """Test image embed with width x height specification."""
        content = "![[image.png|300x200]]"
        result = exporter.convert_to_standard_markdown(content)
        assert result == "![image](image.png)"

    def test_image_embed_with_alt_and_dimensions(self, exporter):
        """Test image embed with alt text and dimensions."""
        content = "![[image.png|description|300x200]]"
        result = exporter.convert_to_standard_markdown(content)
        assert result == "![description](image.png)"

    def test_image_embed_width_before_alt(self, exporter):
        """Test image embed with width before alt text (edge case)."""
        content = "![[image.png|300|description]]"
        result = exporter.convert_to_standard_markdown(content)
        assert result == "![description](image.png)"

    # Wikilink tests
    def test_wikilink_basic(self, exporter):
        """Test basic wiki-link without alias."""
        content = "[[Note Name]]"
        result = exporter.convert_to_standard_markdown(content)
        assert result == "[Note Name](Note Name.md)"

    def test_wikilink_with_alias(self, exporter):
        """Test wiki-link with alias."""
        content = "[[Note Name|Display Name]]"
        result = exporter.convert_to_standard_markdown(content)
        assert result == "[Display Name](Note Name.md)"

    def test_wikilink_with_heading(self, exporter):
        """Test wiki-link with heading reference."""
        content = "[[Note Name#Heading]]"
        result = exporter.convert_to_standard_markdown(content)
        assert result == "[Note Name#Heading](Note Name.md)"

    # Comment tests
    def test_comment_removal(self, exporter):
        """Test that Obsidian comments are removed."""
        content = "Before %%comment%% After"
        result = exporter.convert_to_standard_markdown(content)
        assert result == "Before  After"

    def test_multiline_comment_removal(self, exporter):
        """Test that multiline comments are removed."""
        content = "Before %%multi\nline\ncomment%% After"
        result = exporter.convert_to_standard_markdown(content)
        assert result == "Before  After"

    # Note embed tests
    def test_note_embed_basic(self, exporter):
        """Test note embed converts to link."""
        content = "![[Note Name]]"
        result = exporter.convert_to_standard_markdown(content)
        assert result == "[Note Name](Note Name.md)"

    def test_note_embed_with_alias(self, exporter):
        """Test note embed with alias."""
        content = "![[Note Name|Display Name]]"
        result = exporter.convert_to_standard_markdown(content)
        assert result == "[Display Name](Note Name.md)"

    # Mixed content tests
    def test_mixed_content(self, exporter):
        """Test conversion of mixed content."""
        content = """# Title

Some text with [[Link]] and ![[image.png|description|300]].

%%This is a comment%%

Another [[Page|alias]] here.
"""
        result = exporter.convert_to_standard_markdown(content)
        assert "[Link](Link.md)" in result
        assert "![description](image.png)" in result
        assert "[alias](Page.md)" in result
        assert "%%This is a comment%%" not in result


class TestIsAttachment:
    """Tests for is_attachment method."""

    @pytest.fixture
    def exporter(self, tmp_path):
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        output_path = tmp_path / "output"
        return ObsidianMOCExporter(vault_path, output_path)

    def test_image_extensions(self, exporter):
        """Test image file detection."""
        assert exporter.is_attachment("image.png")
        assert exporter.is_attachment("photo.jpg")
        assert exporter.is_attachment("icon.svg")

    def test_document_extensions(self, exporter):
        """Test document file detection."""
        assert exporter.is_attachment("doc.pdf")
        assert exporter.is_attachment("sheet.xlsx")

    def test_markdown_not_attachment(self, exporter):
        """Test that markdown files are not attachments."""
        assert not exporter.is_attachment("note.md")
        assert not exporter.is_attachment("README.md")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
