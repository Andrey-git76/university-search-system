import type { SearchResponse } from '../types';
import { highlightQuery, sanitizeHighlight } from '../utils/highlight';
import './SearchResults.css';

interface SearchResultsProps {
  data: SearchResponse | null;
  query: string;
  loading: boolean;
  error: string | null;
  onPageChange: (page: number) => void;
}

export default function SearchResults({
  data,
  query,
  loading,
  error,
  onPageChange,
}: SearchResultsProps) {
  if (loading) {
    return <p className="muted-text">Выполняется поиск...</p>;
  }

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (!data) {
    return null;
  }

  if (data.results.length === 0) {
    return (
      <div className="empty-state">
        <p>
          {data.message ||
            'По вашему запросу ничего не найдено. Попробуйте изменить формулировку'}
        </p>
      </div>
    );
  }

  return (
    <section className="results-section">
      <div className="results-header">
        <h3>Результаты поиска</h3>
        <span className="results-count">
          Найдено: {data.total} {data.from_cache ? '(из кеша)' : ''}
        </span>
      </div>

      <ul className="results-list">
        {data.results.map((result) => {
          const content = result.highlight
            ? sanitizeHighlight(result.highlight)
            : highlightQuery(result.text, query);

          return (
            <li key={result.chunk_id} className="result-card">
              <div className="result-card__header">
                <h4>{result.file_name}</h4>
                <span className="result-score">Релевантность: {result.score}</span>
              </div>
              <p className="result-page">Страница {result.page}</p>
              <div
                className="result-text"
                dangerouslySetInnerHTML={{ __html: content }}
              />
            </li>
          );
        })}
      </ul>

      {data.total_pages > 1 && (
        <div className="pagination">
          <button
            type="button"
            className="ghost-button"
            disabled={data.page <= 1}
            onClick={() => onPageChange(data.page - 1)}
          >
            Назад
          </button>
          <span className="pagination__info">
            Страница {data.page} из {data.total_pages}
          </span>
          <button
            type="button"
            className="ghost-button"
            disabled={data.page >= data.total_pages}
            onClick={() => onPageChange(data.page + 1)}
          >
            Вперёд
          </button>
        </div>
      )}
    </section>
  );
}
