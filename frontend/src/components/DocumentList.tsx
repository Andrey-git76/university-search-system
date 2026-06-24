import { useEffect, useState } from 'react';
import type { DocumentInfo } from '../types';
import { deleteDocument, fetchDocuments } from '../services/api';
import './DocumentList.css';

interface DocumentListProps {
  refreshKey: number;
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '—';
  }
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

export default function DocumentList({ refreshKey }: DocumentListProps) {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDocuments();
      setDocuments(data.documents);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadDocuments();
  }, [refreshKey]);

  const handleDelete = async (documentId: string) => {
    setDeletingId(documentId);
    try {
      await deleteDocument(documentId);
      setDocuments((prev) => prev.filter((doc) => doc.document_id !== documentId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось удалить документ');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <section className="documents-section">
      <div className="section-header">
        <h2>Загруженные документы</h2>
        <button type="button" className="ghost-button" onClick={() => void loadDocuments()}>
          Обновить
        </button>
      </div>

      {loading && <p className="muted-text">Загрузка списка...</p>}
      {error && <p className="error-text">{error}</p>}

      {!loading && !error && documents.length === 0 && (
        <p className="muted-text">Документы пока не загружены.</p>
      )}

      {!loading && documents.length > 0 && (
        <ul className="documents-list">
          {documents.map((doc) => (
            <li key={doc.document_id} className="document-card">
              <div className="document-card__content">
                <h3>{doc.file_name}</h3>
                <div className="document-card__meta">
                  <span>Загружен: {formatDate(doc.created_at)}</span>
                  <span>Фрагментов: {doc.chunks_count}</span>
                  <span className="status-badge status-badge--indexed">Проиндексирован</span>
                </div>
              </div>
              <button
                type="button"
                className="danger-button"
                disabled={deletingId === doc.document_id}
                onClick={() => void handleDelete(doc.document_id)}
              >
                {deletingId === doc.document_id ? 'Удаление...' : 'Удалить'}
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
