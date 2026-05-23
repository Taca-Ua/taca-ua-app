import { useRef, useState } from "react";
import Button from "../utils/Button";
import HelpTooltip from "../HelpTooltip";
import { useNotification } from "../../contexts/NotificationProvider";
import { regulationsApi } from "../../api/regulations";
import { useModal } from "../../contexts/ModalContext";
import { useSeason } from "../../contexts/SeasonContext";

const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};


const RegulationCreateModal = ( {
    onCreate,
} : {
    onCreate: (regulation: any) => void;
} ) => {
    const { notify } = useNotification();
    const { popModal } = useModal();
    const { loadedSeason } = useSeason();

    const [ title, setTitle ] = useState("");
    const [ description, setDescription ] = useState("");
    const [ file, setFile ] = useState<File | null>(null);

    const [ isDragOver, setIsDragOver ] = useState(false);
    const [ uploading, setUploading ] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const dragCounterRef = useRef(0);

    const onClose = () => {
        popModal();
        setTitle("");
        setDescription("");
        setFile(null);
        dragCounterRef.current = 0;
        setIsDragOver(false);
        if (fileInputRef.current) fileInputRef.current.value = "";
    };

    const applyFile = (incoming: File | null) => {
        if (!incoming) return;
        if (incoming.type !== 'application/pdf') {
            notify('Apenas ficheiros PDF são permitidos.', 'error');
            return;
        }
        if (incoming.size > 10 * 1024 * 1024) {
            notify('O ficheiro não pode exceder 10 MB.', 'error');
            return;
        }
        setFile(incoming);
    };

    const handleCreate = () => {
        if (!title.trim() || !file) {
            notify('Título e ficheiro são obrigatórios', 'error');
            return;
        }

        setUploading(true);
        regulationsApi.create({
            title,
            file,
            description: description || undefined,
            season_id: loadedSeason?.id,
        }).then(newRegulation => {
            console.log('Regulamento criado:', newRegulation);
            if (onCreate) onCreate(newRegulation);
            notify("Regulamento adicionado com sucesso!", "success");
            onClose();
        }).catch((err: unknown) => {
            console.error('Upload failed:', err);
            if (err instanceof Error) {
                notify(err.message, 'error');
            } else {
                notify('Não foi possível processar o upload do ficheiro.', 'error');
            }
        }).finally(() => {
            setUploading(false);
        });
    };

    return (
        <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold text-gray-800">
              Novo Regulamento
            </h2>
          </div>

          <div className="space-y-5">
            <div className="pt-4">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Título do Documento{" "}
                <HelpTooltip
                  text="Nome identificativo do regulamento. Deve ser claro e descritivo para facilitar a pesquisa. Ex: 'Regulamento de Basquetebol 2026'."
                  className="ml-1"
                />{" "}
                <span className="text-red-500">*</span>
              </label>
              <input
                required
                className="w-full border border-gray-300 px-4 py-2 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Ex: Regulamento de Basquetebol 2026"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Descrição{" "}
                <HelpTooltip
                  text="Informação adicional sobre o documento, como o âmbito de aplicação, alterações face à versão anterior ou notas relevantes. Campo opcional."
                  className="ml-1"
                />
              </label>
              <textarea
                className="w-full border border-gray-300 px-4 py-2 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none min-h-[100px]"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Opcional: detalhes sobre as regras ou atualizações..."
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Ficheiro{" "}
                <HelpTooltip
                  text="Apenas ficheiros PDF são aceites, com tamanho máximo de 10 MB. O ficheiro ficará disponível publicamente para download na página de regulamentos."
                  className="ml-1"
                />{" "}
                <span className="text-red-500">*</span>
              </label>

              {file ? (
                <div className="flex items-center gap-4 p-4 bg-teal-50 border border-teal-200 rounded-xl">
                  {/* PDF badge */}
                  <div className="flex-shrink-0 w-12 h-14 bg-red-100 border border-red-200 rounded-lg flex flex-col items-center justify-center gap-0.5 shadow-sm">
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

                  {/* File metadata */}
                  <div className="flex-1 min-w-0">
                    <p
                      className="font-semibold text-gray-800 text-sm truncate"
                      title={file.name}
                    >
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
                  className={`mt-1 flex flex-col items-center justify-center px-6 py-8 border-2 border-dashed rounded-xl cursor-pointer transition-colors ${
                    isDragOver
                      ? "border-teal-500 bg-teal-50"
                      : "border-gray-300 bg-white hover:border-teal-400 hover:bg-gray-50"
                  }`}
                  onDragOver={e => {
                    e.preventDefault();
                    e.stopPropagation();
                    dragCounterRef.current++;
                    setIsDragOver(true);
                  }}
                  onDragLeave={e => {
                    e.preventDefault();
                    e.stopPropagation();
                    dragCounterRef.current--;
                    if (dragCounterRef.current <= 0) setIsDragOver(false);
                  }}
                  onDrop={e => {
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
                    className={`w-10 h-10 mb-3 transition-colors ${isDragOver ? "text-teal-500" : "text-gray-400"}`}
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
                  <span
                    className={`text-sm font-medium transition-colors ${isDragOver ? "text-teal-600" : "text-teal-600 hover:text-teal-500"}`}
                  >
                    {isDragOver
                      ? "Solte o ficheiro aqui"
                      : "Clique ou arraste um ficheiro PDF"}
                  </span>
                  <span className="text-xs text-gray-400 mt-1">
                    PDF até 10 MB
                  </span>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="application/pdf"
                    className="sr-only"
                    onChange={(e) => applyFile(e.target.files?.[0] ?? null)}
                    required
                  />
                </label>
              )}
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                onClick={onClose}
                type="secondary"
                flexible={true}
              >
                Cancelar
              </Button>
              <Button
                onClick={handleCreate}
                type="primary"
                flexible={true}
                disabled={uploading}
              >
                {uploading ? "A criar..." : "Criar Regulamento"}
              </Button>
            </div>
          </div>
        </div>
    );
}

export default RegulationCreateModal;
