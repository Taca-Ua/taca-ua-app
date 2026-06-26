import { useEffect, useRef, useState } from "react";
import { useNotification } from "../../../contexts/NotificationProvider";

const formatFileSize = (size: number) => {
    if (size < 1024) return `${size} B`;
    else if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`;
    else return `${(size / (1024 * 1024)).toFixed(2)} MB`;
};

const FileInput = ({
  fileState,
  file_url,
  onFileChange,
  fileType = "pdf"
} : {
  fileState: [File | null, React.Dispatch<React.SetStateAction<File | null>>];
  file_url?: string;
  onFileChange?: (file: File | null) => void;
  fileType?: "pdf" | "image";
}) => {
    const { notify } = useNotification();

    const [ file, setFile ] = fileState;
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [ isDragOver, setIsDragOver ] = useState(false);
    const dragCounterRef = useRef(0);

    useEffect(() => {
        if (file_url) {
            // If a file URL is provided, we can fetch the file and set it as the current file.
            fetch(file_url)
                .then(response => response.blob())
                .then(blob => {
                    const fileName = file_url.split('/').pop() || 'downloaded_file.pdf';
                    const file = new File([blob], fileName, { type: blob.type });
                    setFile(file);
                })
                .catch(err => {
                    console.error("Failed to fetch file from URL:", err);
                    notify("Erro ao carregar o ficheiro. Tente novamente.", "error");
                });
        }
    }, [file_url, setFile, notify]);

    const applyFile = (incoming: File | null) => {
        if (!incoming) return;
        if (fileType === "pdf" && incoming.type !== 'application/pdf') {
            notify('Apenas ficheiros PDF são permitidos.', 'error');
            return;
        }
        if (fileType === "image" && !incoming.type.startsWith('image/')) {
            notify('Apenas ficheiros de imagem são permitidos.', 'error');
            return;
        }
        if (incoming.size > 10 * 1024 * 1024) {
            notify('O ficheiro não pode exceder 10 MB.', 'error');
            return;
        }
        setFile(incoming);
        if (onFileChange) onFileChange(incoming);
    };

    return (
      <div>
        {file ? (
          <div className="flex items-center justify-evenly gap-4 p-4 bg-teal-50 border border-teal-200 rounded-xl">
            {/* PDF badge */}

            {fileType === "pdf" && (
              <div className="flex-shrink-0 w-12 h-12 bg-red-100 border border-red-200 rounded-lg flex flex-col items-center justify-center gap-0.5 shadow-sm">
                <svg
                  className="w-5 h-5 text-red-600"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-xs font-bold text-red-600 leading-none">
                  PDF
                </span>
              </div>
            )}

            {fileType === "image" && (
              <div className="flex-shrink-0 w-12 h-12 bg-teal-100 border border-teal-200 rounded-lg flex flex-col items-center justify-center gap-0.5 shadow-sm">
                <img src={URL.createObjectURL(file)} alt="Preview" className="w-10 h-10 object-cover rounded" />
              </div>
            )}

            {/* File metadata */}
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-gray-800 text-sm truncate">
                {file.name}
              </p>
              <p className="text-xs text-gray-500 mt-0.5">
                {formatFileSize(file.size)}
              </p>
            </div>

            <button
              type="button"
              onClick={() => {
                setFile(null);
                if (fileInputRef.current) fileInputRef.current.value = "";
                if (onFileChange) onFileChange(null);
              }}
              className="flex-shrink-0 p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
              title="Remover ficheiro"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        ) : (
          <label
            className={`mt-1 flex p-3 items-center justify-evenly border-2 border-dashed rounded-xl cursor-pointer transition-colors ${
              isDragOver
                ? "border-teal-500 bg-teal-50"
                : "border-gray-300 bg-white hover:border-teal-400 hover:bg-gray-50"
            }`}
            onDragOver={(e) => {
              e.preventDefault();
              e.stopPropagation();
              dragCounterRef.current++;
              setIsDragOver(true);
            }}
            onDragLeave={(e) => {
              e.preventDefault();
              e.stopPropagation();
              dragCounterRef.current--;
              setIsDragOver(false);
            }}
            onDrop={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setIsDragOver(false);
              dragCounterRef.current = 0;
              if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                applyFile(e.dataTransfer.files[0]);
                if (fileInputRef.current) fileInputRef.current.value = "";
              }
            }}
          >
            <svg
              className={`w-10 h-10 transition-colors ${isDragOver ? "text-teal-500" : "text-gray-400"}`}
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div className="flex flex-col items-center justify-center">
                <span
                className={`text-sm font-medium transition-colors ${isDragOver ? "text-teal-600" : "text-teal-600 hover:text-teal-500"}`}
                >
                {isDragOver
                    ? "Solte o ficheiro aqui"
                    : "Clique ou arraste um ficheiro"}
                </span>
                <span className="text-xs text-gray-400 mt-1">Ficheiros até 10 MB</span>
                <input
                ref={fileInputRef}
                type="file"
                accept={fileType === "pdf" ? "application/pdf" : fileType === "image" ? "image/*" : ""}
                className="sr-only"
                onChange={(e) => applyFile(e.target.files?.[0] ?? null)}
                required
                />
            </div>
          </label>
        )}
      </div>
    );
};

export default FileInput;
