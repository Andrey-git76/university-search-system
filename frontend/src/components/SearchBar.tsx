import { useEffect, useState, type FormEvent } from 'react';
import { getSearchHistory } from '../services/api';
import './SearchBar.css';

interface SearchBarProps {
  onSearch: (query: string) => void;
  loading: boolean;
  initialQuery?: string;
}

export default function SearchBar({ onSearch, loading, initialQuery = '' }: SearchBarProps) {
  const [query, setQuery] = useState(initialQuery);
  const [history, setHistory] = useState<string[]>([]);

  useEffect(() => {
    setHistory(getSearchHistory());
  }, [loading]);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || loading) return;
    onSearch(trimmed);
  };

  return (
    <section className="search-section">
      <h2>Поиск по документам</h2>
      <p className="section-description">
        Введите ключевые слова для полнотекстового поиска по загруженным материалам.
      </p>

      <form className="search-form" onSubmit={handleSubmit}>
        <input
          type="search"
          className="search-input"
          placeholder="Например: программирование, база данных..."
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          aria-label="Поисковый запрос"
        />
        <button type="submit" className="primary-button" disabled={loading || !query.trim()}>
          {loading ? 'Поиск...' : 'Найти'}
        </button>
      </form>

      {history.length > 0 && (
        <div className="search-history">
          <span className="search-history__label">История запросов:</span>
          <div className="search-history__items">
            {history.map((item) => (
              <button
                key={item}
                type="button"
                className="history-chip"
                onClick={() => {
                  setQuery(item);
                  onSearch(item);
                }}
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
