from app.utils.chunking import chunk_text


class TestChunkText:
    def test_empty_text_returns_empty_list(self):
        assert chunk_text("") == []

    def test_short_text_returns_single_chunk(self):
        text = "Короткий текст для проверки"
        assert chunk_text(text, chunk_size=1000) == [text]

    def test_long_text_splits_into_multiple_chunks(self):
        text = "Абзац про Москву.\n" * 200
        result = chunk_text(text, chunk_size=100, overlap=20)
        assert len(result) > 1
        assert all(isinstance(chunk, str) for chunk in result)

    def test_chunks_preserve_content(self):
        text = "Первый абзац.\n" + "Второй абзац.\n" * 50
        result = chunk_text(text, chunk_size=80, overlap=10)
        joined = " ".join(result)
        assert "Первый" in joined
        assert "Второй" in joined