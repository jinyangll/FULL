import { UploadCloud, X } from 'lucide-react';
import { useRef, useState } from 'react';
import { validateFile } from '../../lib/validateFile';
import { formatBytes } from '../../lib/formatBytes';

const MAX_FILES = 10;

interface FileUploaderProps {
  files: File[];
  onChange: (files: File[]) => void;
}

export default function FileUploader({ files, onChange }: FileUploaderProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState('');

  const addFiles = (incoming: FileList | null) => {
    if (!incoming || incoming.length === 0) {
      return;
    }
    const next = [...files];
    for (const file of Array.from(incoming)) {
      if (next.length >= MAX_FILES) {
        setError(`최대 ${MAX_FILES}개까지 업로드할 수 있어요.`);
        break;
      }
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        continue;
      }
      const duplicate = next.some((f) => f.name === file.name && f.size === file.size);
      if (!duplicate) {
        next.push(file);
      }
    }
    if (next.length > 0) {
      setError('');
    }
    onChange(next.slice(0, MAX_FILES));
  };

  const removeAt = (index: number) => {
    setError('');
    onChange(files.filter((_, i) => i !== index));
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-4">
      <div
        className={`rounded-2xl border-2 border-dashed p-4 transition sm:p-5 ${
          isDragging ? 'border-brand-accent bg-blue-50/80 shadow-inner' : 'border-slate-300 bg-white'
        } ${error ? 'animate-[shake_180ms_ease-in-out_1] border-red-300 bg-red-50' : ''}`}
        onDragEnter={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={(event) => {
          event.preventDefault();
          setIsDragging(false);
        }}
        onDrop={(event) => {
          event.preventDefault();
          setIsDragging(false);
          addFiles(event.dataTransfer.files);
        }}
      >
        <input
          ref={inputRef}
          className="hidden"
          type="file"
          multiple
          accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
          onChange={(event) => addFiles(event.target.files)}
        />

        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="flex w-full flex-col items-center justify-center gap-5 rounded-xl py-10 text-center transition focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent focus-visible:ring-offset-2"
          aria-label="계약서 및 공적서류 파일 선택"
        >
          <span className="flex h-16 w-16 items-center justify-center rounded-2xl border border-slate-200 bg-slate-50 text-brand shadow-sm">
            <UploadCloud size={30} aria-hidden="true" />
          </span>
          <span>
            <span className="block break-keep text-base font-bold text-brand">
              계약서와 관련 공적서류를 업로드하세요
            </span>
            <span className="mt-2 block text-sm text-brand-muted">
              PDF, JPG, PNG · 최대 {MAX_FILES}개 · 계약서는 필수
            </span>
          </span>
        </button>
      </div>

      {files.length > 0 ? (
        <ul className="space-y-2">
          {files.map((file, index) => (
            <li
              key={`${file.name}-${file.size}`}
              className="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-brand">{file.name}</p>
                <p className="text-xs text-brand-muted">{formatBytes(file.size)}</p>
              </div>
              <button
                type="button"
                onClick={() => removeAt(index)}
                className="shrink-0 rounded-lg p-1 text-brand-muted hover:bg-slate-100 hover:text-brand"
                aria-label={`${file.name} 제거`}
              >
                <X size={16} aria-hidden="true" />
              </button>
            </li>
          ))}
        </ul>
      ) : null}

      {error ? <p className="text-sm font-semibold text-red-700">{error}</p> : null}
    </div>
  );
}
