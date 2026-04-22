import { useEffect, useRef, useState } from "react";
import Button from "../utils/Button";
import HelpTooltip from "../HelpTooltip";
import { useNotification } from "../../contexts/NotificationProvider";
import { regulationsApi, type RegulationDetail } from "../../api/regulations";

const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

const RegulationEditModal = ( {
    controller,
    regulationState,
    onSave
} : {
    controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>]
    regulationState: [RegulationDetail, React.Dispatch<React.SetStateAction<RegulationDetail | null>>]
    onSave?: (regulation: RegulationDetail) => void
} ) => {
    const [ isOpen, setIsOpen ] = controller;
    const [ regulation, setRegulation ] = regulationState;
    const { notify } = useNotification();

    const [ title, setTitle ] = useState("");
    const [ description, setDescription ] = useState("");
    const [ file, setFile ] = useState<File | null>(null);
    const [ isDragOver, setIsDragOver ] = useState(false);
    const [ uploading, setUploading ] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const dragCounterRef = useRef(0);

    useEffect(() => {
        if (!isOpen) return;

        setTitle(regulation.title);
        setDescription(regulation.description || "");
        setFile(null);
    }, [regulation, isOpen]);

    const onClose = () => {
        if ( uploading ) return;

        setTitle(regulation.title);
        setDescription(regulation.description || "");
        setFile(null);
        setIsDragOver(false);
        setIsOpen(false);
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

    const handleEdit = () => {
      setUploading(true);
      regulationsApi.update(regulation.id, {
          title:title,
          description:description,
          file:file? file : undefined
      }).then( (data) => {
        setRegulation(data);
        if (onSave) onSave(data);
        onClose();
        notify('Regulamento editado com sucesso.', 'success');
      } ).catch( () => {
        notify('Ocorreu um erro ao editar o regulamento.', 'error');
      } ).finally( () => {
        setUploading(false);
      } );
    }

    if ( !isOpen ) return null;

    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-50 p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in duration-200">
          <div className="p-6 border-b border-gray-100 flex justify-between items-center">
            <h2 className="text-xl font-bold text-gray-800">
              Editar Regulamento
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          <div className="p-6 space-y-5">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Título do Documento{" "}
                <HelpTooltip
                  text="Nome identificativo do regulamento. Deve ser claro e descritivo para facilitar a pesquisa. Ex: 'Regulamento de Basquetebol 2026'."
                  className="ml-1"
                />
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
                />
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
                onClick={handleEdit}
                type="primary"
                flexible={true}
                disabled={uploading}
              >
                {uploading ? "A editar..." : "Editar Regulamento"}
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
}

export default RegulationEditModal;
