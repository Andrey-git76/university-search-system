from unittest.mock import AsyncMock, patch

import pytest


class TestDocumentsUpload:
    def test_upload_rejects_wrong_format(self, api_client, fixtures_dir):
        with open(fixtures_dir / "wrong_format.txt", "rb") as f:
            response = api_client.post(
                "/api/v1/documents/upload",
                files={"file": ("report.txt", f, "text/plain")},
            )

        assert response.status_code == 400
        assert "Unsupported format" in response.json()["detail"]

    def test_upload_rejects_corrupted_pdf(self, api_client, fixtures_dir):
        with open(fixtures_dir / "corrupted.pdf", "rb") as f:
            response = api_client.post(
                "/api/v1/documents/upload",
                files={"file": ("bad.pdf", f, "application/pdf")},
            )

        assert response.status_code == 500
        assert "Error processing document" in response.json()["detail"]

    def test_upload_rejects_empty_pdf(self, api_client, fixtures_dir):
        with open(fixtures_dir / "empty.pdf", "rb") as f:
            response = api_client.post(
                "/api/v1/documents/upload",
                files={"file": ("empty.pdf", f, "application/pdf")},
            )

        assert response.status_code == 400
        assert "No text could be extracted" in response.json()["detail"]

    def test_upload_rejects_oversized_file(self, api_client):
        """Загрузка файла размером больше лимита"""
        # Генерируем файл размером 2 КБ (это быстро передаётся)
        file_content = b"0" * (2 * 1024)

        # Устанавливаем лимит в 1 КБ (меньше, чем файл)
        with patch('app.api.v1.endpoints.documents.settings.MAX_FILE_SIZE_MB', 0.001):
            response = api_client.post(
                "/api/v1/documents/upload",
                files={"file": ("huge.pdf", file_content, "application/pdf")},
            )

        assert response.status_code == 400
        assert "maximum size" in response.json()["detail"].lower()

    @patch("app.api.v1.endpoints.documents.IndexManager")
    def test_upload_success_pdf(self, MockIndexer, api_client, valid_pdf_bytes):
        mock_indexer = AsyncMock()
        mock_indexer.index_chunks = AsyncMock()
        MockIndexer.return_value = mock_indexer

        response = api_client.post(
            "/api/v1/documents/upload",
            files={"file": ("valid.pdf", valid_pdf_bytes, "application/pdf")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "indexed"
        assert data["file_name"] == "valid.pdf"
        assert data["chunks_count"] > 0
        assert "document_id" in data

        mock_indexer.index_chunks.assert_awaited_once()
        call_args = mock_indexer.index_chunks.await_args
        document_id = call_args.kwargs.get("document_id") or call_args.args[0]
        file_name = call_args.kwargs.get("file_name") or call_args.args[1]
        chunks = call_args.kwargs.get("chunks") or call_args.args[2]

        assert document_id == data["document_id"]
        assert file_name == "valid.pdf"
        assert len(chunks) == data["chunks_count"]
        assert all("chunk_id" in chunk and chunk["text"] for chunk in chunks)

    @patch("app.api.v1.endpoints.documents.IndexManager")
    def test_upload_success_docx(self, MockIndexer, api_client, valid_docx_bytes):
        mock_indexer = AsyncMock()
        mock_indexer.index_chunks = AsyncMock()
        MockIndexer.return_value = mock_indexer

        response = api_client.post(
            "/api/v1/documents/upload",
            files={
                "file": (
                    "valid.docx",
                    valid_docx_bytes,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "indexed"
        assert data["file_name"] == "valid.docx"
        assert data["chunks_count"] > 0

        call_args = mock_indexer.index_chunks.await_args
        file_name = call_args.kwargs.get("file_name") or call_args.args[1]
        chunks = call_args.kwargs.get("chunks") or call_args.args[2]
        assert file_name == "valid.docx"
        assert len(chunks) == data["chunks_count"]

    @patch("app.api.v1.endpoints.documents.IndexManager")
    def test_upload_success_rare_fonts_pdf(self, MockIndexer, api_client, rare_fonts_pdf_bytes):
        """Загрузка PDF с нестандартными шрифтами."""
        mock_indexer = AsyncMock()
        mock_indexer.index_chunks = AsyncMock()
        MockIndexer.return_value = mock_indexer

        response = api_client.post(
            "/api/v1/documents/upload",
            files={"file": ("rare_fonts.pdf", rare_fonts_pdf_bytes, "application/pdf")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "indexed"
        assert data["file_name"] == "rare_fonts.pdf"
        assert data["chunks_count"] > 0

    @patch("app.api.v1.endpoints.documents.IndexManager")
    def test_upload_success_rare_fonts_docx(
        self, MockIndexer, api_client, rare_fonts_docx_bytes
    ):
        """Загрузка DOCX с нестандартными шрифтами."""
        mock_indexer = AsyncMock()
        mock_indexer.index_chunks = AsyncMock()
        MockIndexer.return_value = mock_indexer

        response = api_client.post(
            "/api/v1/documents/upload",
            files={
                "file": (
                    "rare_fonts.docx",
                    rare_fonts_docx_bytes,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "indexed"
        assert data["file_name"] == "rare_fonts.docx"
        assert data["chunks_count"] > 0

    @patch("app.api.v1.endpoints.documents.IndexManager")
    def test_upload_empty_docx_returns_zero_chunks(
        self, MockIndexer, api_client, empty_docx_bytes
    ):
        mock_indexer = AsyncMock()
        mock_indexer.index_chunks = AsyncMock()
        MockIndexer.return_value = mock_indexer

        response = api_client.post(
            "/api/v1/documents/upload",
            files={
                "file": (
                    "empty.docx",
                    empty_docx_bytes,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "indexed"
        assert data["chunks_count"] == 0

        call_args = mock_indexer.index_chunks.await_args
        if "chunks" in call_args.kwargs:
            chunks = call_args.kwargs["chunks"]
        else:
            chunks = call_args.args[2]
        assert chunks == []


class TestDocumentsList:
    @patch("app.api.v1.endpoints.documents.IndexManager")
    def test_list_documents(self, MockIndexer, api_client):
        mock_instance = AsyncMock()
        mock_instance.list_documents = AsyncMock(
            return_value=[
                {
                    "document_id": "doc-1",
                    "file_name": "valid.pdf",
                    "chunks_count": 5,
                    "created_at": "2025-01-15T10:00:00",
                }
            ]
        )
        mock_instance.get_total_documents = AsyncMock(return_value=1)
        MockIndexer.return_value = mock_instance

        response = api_client.get("/api/v1/documents")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["total"] == 1
        assert data["documents"][0]["file_name"] == "valid.pdf"


class TestDocumentsDelete:
    @patch("app.api.v1.endpoints.documents.IndexManager")
    def test_delete_not_found(self, MockIndexer, api_client):
        mock_instance = AsyncMock()
        mock_instance.delete_document = AsyncMock(return_value=False)
        MockIndexer.return_value = mock_instance

        response = api_client.delete("/api/v1/documents/nonexistent-id")

        assert response.status_code == 404

    @patch("app.api.v1.endpoints.documents.IndexManager")
    def test_delete_success(self, MockIndexer, api_client):
        mock_instance = AsyncMock()
        mock_instance.delete_document = AsyncMock(return_value=True)
        MockIndexer.return_value = mock_instance

        response = api_client.delete("/api/v1/documents/doc-uuid-1")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deleted"
        assert data["document_id"] == "doc-uuid-1"
        mock_instance.delete_document.assert_called_once_with("doc-uuid-1")
