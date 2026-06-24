export interface DocumentInfo {
  document_id: string;
  file_name: string;
  chunks_count: number;
  created_at: string;
}

export interface DocumentsResponse {
  documents: DocumentInfo[];
  count: number;
  total: number;
}

export interface UploadResponse {
  document_id: string;
  file_name: string;
  chunks_count: number;
  status: string;
  message?: string;
}

export interface SearchResult {
  chunk_id: string;
  file_name: string;
  page: number;
  text: string;
  score: number;
  highlight?: string | null;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  count: number;
  total: number;
  page: number;
  total_pages: number;
  from_cache: boolean;
  message?: string;
}

export type UploadStatus = 'pending' | 'uploading' | 'indexing' | 'done' | 'error';

export interface UploadItem {
  id: string;
  file: File;
  status: UploadStatus;
  progress: number;
  error?: string;
  documentId?: string;
}
