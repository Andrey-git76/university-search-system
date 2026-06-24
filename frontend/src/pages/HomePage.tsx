import { useCallback, useState } from 'react';
import FileUpload from '../components/FileUpload';
import DocumentList from '../components/DocumentList';
import SearchBar from '../components/SearchBar';
import SearchResults from '../components/SearchResults';
import type { SearchResponse } from '../types';
import { saveSearchQuery, searchDocuments } from '../services/api';
import './HomePage.css';

const PAGE_SIZE = 10;

export default function HomePage() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchData, setSearchData] = useState<SearchResponse | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  const performSearch = useCallback(async (query: string, page = 1) => {
    setSearchLoading(true);
    setSearchError(null);
    setSearchQuery(query);

    try {
      const offset = (page - 1) * PAGE_SIZE;
      const data = await searchDocuments(query, PAGE_SIZE, offset);
      setSearchData(data);
      saveSearchQuery(query);
    } catch (error) {
      setSearchData(null);
      setSearchError(error instanceof Error ? error.message : 'Ошибка поиска');
    } finally {
      setSearchLoading(false);
    }
  }, []);

  const handleUploadComplete = () => {
    setRefreshKey((value) => value + 1);
  };

  return (
    <div className="home-page">
      <header className="hero">
        <div className="hero__content">
          <p className="hero__badge">University Search System</p>
          <h1>Поиск по базе знаний университета</h1>
          <p className="hero__subtitle">
            Загружайте учебные материалы в формате PDF и DOCX и выполняйте полнотекстовый поиск с подсветкой совпадений.
          </p>
        </div>
      </header>

      <main className="content-grid">
        <div className="content-column">
          <FileUpload onUploadComplete={handleUploadComplete} />
          <DocumentList refreshKey={refreshKey} />
        </div>

        <div className="content-column">
          <SearchBar
            onSearch={(query) => void performSearch(query, 1)}
            loading={searchLoading}
            initialQuery={searchQuery}
          />
          <SearchResults
            data={searchData}
            query={searchQuery}
            loading={searchLoading}
            error={searchError}
            onPageChange={(page) => void performSearch(searchQuery, page)}
          />
        </div>
      </main>
    </div>
  );
}
