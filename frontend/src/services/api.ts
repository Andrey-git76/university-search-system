import type {
  DocumentsResponse,
  SearchResponse,
  UploadResponse,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchDocuments(): Promise<DocumentsResponse> {
  const response = await fetch(`${API_BASE}/api/v1/documents`);
  if (!response.ok) {
    throw new Error('Не удалось загрузить список документов');
  }
  return response.json();
}

export async function deleteDocument(documentId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/v1/documents/${documentId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || 'Не удалось удалить документ');
  }
}

export function uploadDocument(
  file: File,
  onProgress: (progress: number, phase: 'uploading' | 'indexing') => void
): Promise<UploadResponse> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append('file', file);

    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const percent = Math.round((event.loaded / event.total) * 100);
        onProgress(percent, 'uploading');
      }
    });

    xhr.upload.addEventListener('load', () => {
      onProgress(100, 'indexing');
    });

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        try {
          const data = JSON.parse(xhr.responseText);
          reject(new Error(data.detail || 'Ошибка загрузки файла'));
        } catch {
          reject(new Error('Ошибка загрузки файла'));
        }
      }
    });

    xhr.addEventListener('error', () => {
      reject(new Error('Сетевая ошибка при загрузке файла'));
    });

    xhr.open('POST', `${API_BASE}/api/v1/documents/upload`);
    xhr.send(formData);
  });
}

export async function searchDocuments(
  query: string,
  limit = 10,
  offset = 0
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    limit: String(limit),
    offset: String(offset),
  });

  const response = await fetch(`${API_BASE}/api/v1/search?${params}`);
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || 'Ошибка поиска');
  }
  return response.json();
}

export const SEARCH_HISTORY_KEY = 'university-search-history';

export function getSearchHistory(): string[] {
  try {
    const raw = localStorage.getItem(SEARCH_HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveSearchQuery(query: string): void {
  const trimmed = query.trim();
  if (!trimmed) return;

  const history = getSearchHistory().filter((item) => item !== trimmed);
  history.unshift(trimmed);
  localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(history.slice(0, 10)));
}
