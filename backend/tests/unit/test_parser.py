import pytest

from app.services.parser import DocumentParser


@pytest.mark.asyncio
class TestDocumentParserPdf:
    async def test_parse_valid_pdf_extracts_text(self, valid_pdf_bytes):
        pages = await DocumentParser.parse_pdf(valid_pdf_bytes)

        assert len(pages) >= 1
        full_text = " ".join(p["text"] for p in pages)
        assert "Москва" in full_text
        assert "Кремль" in full_text
        assert all(p["page"] >= 1 for p in pages)

    async def test_parse_empty_pdf_returns_no_pages(self, fixtures_dir):
        content = (fixtures_dir / "empty.pdf").read_bytes()
        pages = await DocumentParser.parse_pdf(content)
        assert pages == []

    async def test_parse_corrupted_pdf_raises(self, fixtures_dir):
        content = (fixtures_dir / "corrupted.pdf").read_bytes()
        with pytest.raises(Exception, match=r"(?i)pdf"):
            await DocumentParser.parse_pdf(content)

    async def test_parse_rare_fonts_pdf_extracts_special_symbols(self, rare_fonts_pdf_bytes):
        """QA-03: парсинг PDF с нестандартными шрифтами и символами."""
        pages = await DocumentParser.parse_pdf(rare_fonts_pdf_bytes)

        assert len(pages) >= 1
        full_text = " ".join(p["text"] for p in pages)
        assert "нестандартными шрифтами" in full_text
        assert any(symbol in full_text for symbol in ("∑", "α", "ї", "€"))

    async def test_parse_rare_fonts_pdf_produces_indexable_chunks(self, rare_fonts_pdf_bytes):
        pages = await DocumentParser.parse_pdf(rare_fonts_pdf_bytes)
        chunks = DocumentParser.chunk_pages(pages, chunk_size=200, overlap=20)

        assert len(chunks) >= 1
        assert all(chunk["text"].strip() for chunk in chunks)


@pytest.mark.asyncio
class TestDocumentParserDocx:
    async def test_parse_valid_docx_extracts_text(self, valid_docx_bytes):
        pages = await DocumentParser.parse_docx(valid_docx_bytes)

        assert len(pages) == 1
        assert pages[0]["page"] == 1
        text = pages[0]["text"]
        assert text.strip()
        assert len(text.split()) > 5

    async def test_parse_empty_docx_returns_empty_text(self, empty_docx_bytes):
        pages = await DocumentParser.parse_docx(empty_docx_bytes)
        assert len(pages) == 1
        assert pages[0]["text"] == ""

    async def test_parse_rare_fonts_docx_extracts_special_symbols(self, rare_fonts_docx_bytes):
        """QA-03: парсинг DOCX с нестандартными шрифтами и символами."""
        pages = await DocumentParser.parse_docx(rare_fonts_docx_bytes)

        assert len(pages) == 1
        text = pages[0]["text"]
        assert "нестандартными шрифтами" in text
        assert any(symbol in text for symbol in ("∑", "α", "ї", "€"))
        assert any(font in text for font in ("Cambria Math", "Segoe UI Symbol"))


@pytest.mark.asyncio
class TestDocumentParserChunkPages:
    async def test_chunk_pages_creates_unique_ids(self):
        pages = [{"page": 1, "text": " ".join(["слово"] * 1500)}]
        chunks = DocumentParser.chunk_pages(pages, chunk_size=500, overlap=50)

        assert len(chunks) >= 2
        assert all("chunk_id" in c and "page" in c and "text" in c for c in chunks)
        ids = [c["chunk_id"] for c in chunks]
        assert len(ids) == len(set(ids))

    async def test_chunk_pages_empty_input(self):
        assert DocumentParser.chunk_pages([]) == []

    async def test_chunk_pages_valid_pdf_content(self, valid_pdf_bytes):
        pages = await DocumentParser.parse_pdf(valid_pdf_bytes)
        chunks = DocumentParser.chunk_pages(pages, chunk_size=100, overlap=10)

        assert len(chunks) >= 1
        combined = " ".join(c["text"] for c in chunks)
        assert "МГУ" in combined or "Москва" in combined
