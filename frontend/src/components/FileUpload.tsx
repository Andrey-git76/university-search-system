import { useCallback, useRef, useState } from 'react';
import type { UploadItem } from '../types';
import { uploadDocument } from '../services/api';
import './FileUpload.css';

interface FileUploadProps {
  onUploadComplete: () => void;
}

const ALLOWED_EXTENSIONS = ['.pdf', '.docx'];
const MAX_SIZE_MB = 20;

function getFileExtension(name: string): string {
  const index = name.lastIndexOf('.');
  return index >= 0 ? name.slice(index).toLowerCase() : '';
}

function createUploadItem(file: File): UploadItem {
  return {
    id: `${file.name}-${file.size}-${Date.now()}-${Math.random()}`,
    file,
    status: 'pending',
    progress: 0,
  };
}

export default function FileUpload({ onUploadComplete }: FileUploadProps) {
  const [uploads, setUploads] = useState<UploadItem[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const updateUpload = useCallback((id: string, patch: Partial<UploadItem>) => {
    setUploads((prev) =>
      prev.map((item) => (item.id === id ? { ...item, ...patch } : item))
    );
  }, []);

  const processFile = useCallback(
    async (file: File) => {
      const extension = getFileExtension(file.name);

      if (!ALLOWED_EXTENSIONS.includes(extension)) {
        const item = createUploadItem(file);
        setUploads((prev) => [
          { ...item, status: 'error', error: 'Поддерживаются только PDF и DOCX' },
          ...prev,
        ]);
        return;
      }

      if (file.size > MAX_SIZE_MB * 1024 * 1024) {
        const item = createUploadItem(file);
        setUploads((prev) => [
          { ...item, status: 'error', error: `Размер файла не более ${MAX_SIZE_MB} МБ` },
          ...prev,
        ]);
        return;
      }

      const item = createUploadItem(file);
      setUploads((prev) => [{ ...item, status: 'uploading' }, ...prev]);

      try {
        const result = await uploadDocument(file, (progress, phase) => {
          updateUpload(item.id, {
            status: phase === 'uploading' ? 'uploading' : 'indexing',
            progress: phase === 'uploading' ? progress : 100,
          });
        });

        updateUpload(item.id, {
          status: 'done',
          progress: 100,
          documentId: result.document_id,
        });
        onUploadComplete();
      } catch (error) {
        updateUpload(item.id, {
          status: 'error',
          progress: 0,
          error: error instanceof Error ? error.message : 'Неизвестная ошибка',
        });
      }
    },
    [onUploadComplete, updateUpload]
  );

  const handleFiles = useCallback(
    (fileList: FileList | null) => {
      if (!fileList) return;
      Array.from(fileList).forEach((file) => {
        void processFile(file);
      });
    },
    [processFile]
  );

  const onDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    handleFiles(event.dataTransfer.files);
  };

  const statusLabel: Record<UploadItem['status'], string> = {
    pending: 'Ожидание...',
    uploading: 'Загрузка...',
    indexing: 'Индексация...',
    done: 'Готово',
    error: 'Ошибка',
  };

  return (
    <section className="upload-section">
      <h2>Загрузка документов</h2>
      <p className="section-description">
        Перетащите PDF или DOCX файлы сюда или выберите их на компьютере. Максимальный размер — 20 МБ.
      </p>

      <div
        className={`dropzone ${isDragging ? 'dropzone--active' : ''}`}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            inputRef.current?.click();
          }
        }}
      >
        <div className="dropzone__icon">📄</div>
        <p className="dropzone__title">Перетащите файлы сюда</p>
        <p className="dropzone__subtitle">или нажмите для выбора</p>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          multiple
          hidden
          onChange={(event) => {
            handleFiles(event.target.files);
            event.target.value = '';
          }}
        />
      </div>

      {uploads.length > 0 && (
        <ul className="upload-list">
          {uploads.map((item) => (
            <li key={item.id} className={`upload-item upload-item--${item.status}`}>
              <div className="upload-item__header">
                <span className="upload-item__name">{item.file.name}</span>
                <span className="upload-item__status">{statusLabel[item.status]}</span>
              </div>

              {item.status !== 'error' && item.status !== 'done' && (
                <div className="progress-bar">
                  <div
                    className="progress-bar__fill"
                    style={{ width: `${item.progress}%` }}
                  />
                </div>
              )}

              {item.error && <p className="upload-item__error">{item.error}</p>}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
