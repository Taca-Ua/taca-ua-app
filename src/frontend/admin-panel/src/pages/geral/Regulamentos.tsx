import { useState, useEffect, useRef } from "react";
import { regulationsApi, type RegulationListItem as Regulation } from '../../api/regulations';
import { useNotification } from '../../contexts/NotificationProvider';
import { useAuth } from "../../hooks/useAuth";
import RegulationCreateModal from "../../components/regulations/RegulationCreateModal";
import RegulationInfoModal from "../../components/regulations/RegulationInfoModal";
import { useModal } from "../../contexts/ModalContext";
import Button from "../../components/utils/Button";
import { useSeason } from "../../contexts/SeasonContext";
import SeasonSelector from "../../components/seasons/SeasonSelector";

const formatDisplayDate = (dateStr: string | undefined) => {
    if (!dateStr) return "Data indisponível";

    const date = new Date(dateStr);

    if (isNaN(date.getTime())) {
      const fallbackDate = new Date(dateStr.split('.')[0] + 'Z');
      if (isNaN(fallbackDate.getTime())) return "Data indisponível";
      return fallbackDate.toLocaleDateString('pt-PT', { day: '2-digit', month: 'long', year: 'numeric' });
    }

    return date.toLocaleDateString('pt-PT', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
};

const Regulamentos = () => {
  const [regulations, setRegulations] = useState<Regulation[]>([]);
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();
  const { isAdminGeneral } = useAuth();
  const { pushModal } = useModal();
  const { loadedSeason } = useSeason();

  const [searchTerm, setSearchTerm] = useState("");

  // Remove global drag state and file state, handle drag events only on main area
  const mainRef = useRef<HTMLDivElement>(null);
  const dragCounterRef = useRef(0);

  useEffect(() => {
    const main = mainRef.current;
    if (!main) return;

    const onDragEnter = (e: DragEvent) => {
      e.preventDefault();
      dragCounterRef.current++;
      // Only show modal if dragging a file
      const hasFile = Array.from(e.dataTransfer?.items ?? []).some(i => i.kind === 'file');
      if (hasFile && isAdminGeneral) {
        pushModal(
          <RegulationCreateModal
            onCreate={(newRegulation) => setRegulations(prev => [newRegulation, ...prev])}
          />
        );
      }
    };
    const onDragOver = (e: DragEvent) => {
      e.preventDefault();
    };
    const onDragLeave = (e: DragEvent) => {
      e.preventDefault();
      dragCounterRef.current = Math.max(0, dragCounterRef.current - 1);
    };
    const onDrop = (e: DragEvent) => {
      e.preventDefault();
      dragCounterRef.current = 0;
    };
    main.addEventListener('dragenter', onDragEnter);
    main.addEventListener('dragover', onDragOver);
    main.addEventListener('dragleave', onDragLeave);
    main.addEventListener('drop', onDrop);
    return () => {
      main.removeEventListener('dragenter', onDragEnter);
      main.removeEventListener('dragover', onDragOver);
      main.removeEventListener('dragleave', onDragLeave);
      main.removeEventListener('drop', onDrop);
    };
  }, [isAdminGeneral]);

  useEffect(() => {
    setLoading(true);
    regulationsApi.getAll({
      season_id: loadedSeason?.id
    }).then(data => {
      setRegulations(data);
      setLoading(false);
    }).catch((err: unknown) => {
      console.error('Failed to fetch regulations:', err);
      notify('Failed to load regulations.', 'error');
      setLoading(false);
    });
  }, [loadedSeason?.id]);

  const filteredRegulations = regulations
    .filter(r => r.title.toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => a.title.localeCompare(b.title));

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-teal-500 border-t-transparent"></div>
        <p className="mt-4 text-gray-600 font-medium">A sincronizar com o servidor...</p>
      </div>
    );
  }

  return (
    <div ref={mainRef}>
      <SeasonSelector />
      <div className="flex-1 p-8" >
        <div className="max-w-7xl mx-auto">

          <header className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Gestão de Regulamentos</h1>
              <p className="text-gray-500 mt-1">Consulte e gira os documentos oficiais do sistema.</p>
            </div>

            <Button
              onClick={() => pushModal(
                <RegulationCreateModal
                  onCreate={(newRegulation) => setRegulations(prev => [newRegulation, ...prev])}
                />
              )}
              type="primary"
              active={isAdminGeneral}
            >
              + Novo Regulamento
            </Button>
          </header>

          {/* Barra de Ferramentas */}
          <div className="flex gap-3 mb-6">
            <input
              type="text"
              placeholder="Pesquisar regulamento..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Grid de Cards / Lista com Teu Loading */}
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="h-12 w-12 animate-spin rounded-full border-4 border-teal-500 border-t-transparent"></div>
              <p className="mt-4 text-gray-600 font-medium">A sincronizar com o servidor...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredRegulations.length > 0 ? (
                filteredRegulations.map(reg => (
                  <div
                    key={reg.id}
                    onClick={() => pushModal(
                      <RegulationInfoModal
                        regulationId={reg.id}
                        onEditSuccess={(updatedRegulation) => {
                          setRegulations(prev => prev.map(r => r.id === updatedRegulation.id ? updatedRegulation : r));
                        }}
                        onDelete={() => {
                          setRegulations(prev => prev.filter(r => r.id !== reg.id));
                        }}
                      />
                    )}
                    className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm hover:shadow-md hover:border-teal-300 transition-all cursor-pointer group"
                  >
                    <div className="flex items-start justify-between">
                      <div className="p-2 bg-teal-50 rounded-lg group-hover:bg-teal-100 transition-colors">
                        <svg className="w-6 h-6 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                      </div>
                      <span className="text-xs text-gray-400 font-mono">PDF</span>
                    </div>
                    <h3 className="mt-4 font-bold text-gray-900 line-clamp-1">{reg.title}</h3>
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2 min-h-[40px]">
                      {reg.description || "Sem descrição disponível."}
                    </p>
                    <div className="mt-4 pt-4 border-t border-gray-50 flex justify-between items-center text-xs text-gray-400">
                       <span>
                        {formatDisplayDate(reg.created_at)}
                       </span>
                       <span className="text-teal-600 font-semibold">Ver detalhes →</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-full bg-white py-12 rounded-xl border-2 border-dashed border-gray-200 text-center">
                  <p className="text-gray-500">Nenhum documento encontrado para a sua pesquisa.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Regulamentos;
