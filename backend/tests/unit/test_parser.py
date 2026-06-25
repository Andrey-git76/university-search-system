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
