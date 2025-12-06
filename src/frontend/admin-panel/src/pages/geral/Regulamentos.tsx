import { useState, useEffect } from "react";
import Sidebar from "../../components/geral_navbar";
import { regulationsApi, type Regulation, type RegulationCreate } from '../../api/regulations';
import { modalitiesApi, type Modality } from '../../api/modalities';

const Regulamentos = () => {
  const [regulations, setRegulations] = useState<Regulation[]>([]);
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterModality, setFilterModality] = useState("");
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [selectedRegulation, setSelectedRegulation] = useState<Regulation | null>(null);

  // Campos Upload
  const [title, setTitle] = useState("");
  const [modalityId, setModalityId] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [regulationsData, modalitiesData] = await Promise.all([
        regulationsApi.getAll(),
        modalitiesApi.getAll(),
      ]);
      setRegulations(regulationsData);
      setModalities(modalitiesData);
      setError('');
    } catch (err) {
      console.error('Failed to fetch data:', err);
      setError('Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  const filtered = regulations.filter(r =>
    (!filterModality || String(r.modality_id) === filterModality)
  );

  const getModalityName = (modalityId?: number) => {
    if (!modalityId) return "—";
    const modality = modalities.find(m => m.id === modalityId);
    return modality ? modality.name : `Modalidade ${modalityId}`;
  };

  const handleUpload = async () => {
    if (!title.trim() || !file) {
      alert("Título e ficheiro são obrigatórios");
      return;
    }

    try {
      setError('');
      const newRegulationData: RegulationCreate = {
        file,
        title,
        modality_id: modalityId ? Number(modalityId) : undefined,
        description: description || undefined,
      };

      const newRegulation = await regulationsApi.create(newRegulationData);
      setRegulations([...regulations, newRegulation]);

      // reset
      setTitle("");
      setModalityId("");
      setDescription("");
      setFile(null);
      setIsUploadModalOpen(false);
    } catch (err: unknown) {
      console.error('Failed to upload regulation:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Erro ao fazer upload do regulamento');
      }
    }
  };

  const handleViewRegulation = (regulation: Regulation) => {
    setSelectedRegulation(regulation);
    setIsViewModalOpen(true);
  };

  const handleDelete = async () => {
    if (!selectedRegulation) return;

    if (!confirm(`Tem certeza que deseja eliminar "${selectedRegulation.title}"?`)) {
      return;
    }

    try {
      setError('');
      await regulationsApi.delete(selectedRegulation.id);
      setRegulations(regulations.filter(r => r.id !== selectedRegulation.id));
      setIsViewModalOpen(false);
      setSelectedRegulation(null);
      alert('Regulamento eliminado com sucesso!');
    } catch (err: unknown) {
      console.error('Failed to delete regulation:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Erro ao eliminar regulamento');
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8 max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Regulamentos</h1>

          <button
            onClick={() => setIsUploadModalOpen(true)}
            className="px-6 py-3 bg-teal-500 text-white rounded-md hover:bg-teal-600"
          >
            + Adicionar Regulamento
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {error}
          </div>
        )}

        {/* Filtros */}
        <div className="flex gap-6 mb-6">
          <div>
            <label className="block mb-1 font-medium text-gray-700">Modalidade</label>
            <select
              className="border px-3 py-2 rounded-md bg-white"
              value={filterModality}
              onChange={e => setFilterModality(e.target.value)}
            >
              <option value="">Todas</option>
              {modalities.map(m => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Lista */}
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-teal-500 border-r-transparent"></div>
              <p className="mt-2 text-gray-600">A carregar...</p>
            </div>
          ) : filtered.length > 0 ? (
            filtered.map(r => (
              <div
                key={r.id}
                className="p-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer flex justify-between items-center"
                onClick={() => handleViewRegulation(r)}
              >
                <div>
                  <div className="font-medium">{r.title}</div>
                  {r.description && (
                    <div className="text-sm text-gray-600 mt-1">{r.description}</div>
                  )}
                </div>
                <div className="text-gray-600 text-sm">
                  {getModalityName(r.modality_id)}
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center">Nenhum regulamento encontrado.</p>
          )}
        </div>

      </div>

      {/* ========== MODAL UPLOAD ========== */}
      {isUploadModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white p-8 rounded-lg w-full max-w-md">

            <h2 className="text-2xl font-bold mb-6">Upload Regulamento</h2>

            <div className="space-y-4">

              <div>
                <label className="font-medium">Título<span className="text-red-500">*</span></label>
                <input
                  className="border px-3 py-2 rounded-md w-full"
                  value={title}
                  onChange={e => setTitle(e.target.value)}
                />
              </div>

              <div>
                <label className="font-medium">Modalidade</label>
                <select
                  className="border px-3 py-2 rounded-md w-full bg-white"
                  value={modalityId}
                  onChange={e => setModalityId(e.target.value)}
                >
                  <option value="">Nenhuma (Geral)</option>
                  {modalities.map(m => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="font-medium">Descrição</label>
                <textarea
                  className="border px-3 py-2 rounded-md w-full"
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                />
              </div>

              <div>
                <label className="font-medium">Ficheiro<span className="text-red-500">*</span></label>
                <input
                  type="file"
                  className="border px-3 py-2 rounded-md w-full"
                  onChange={e => setFile(e.target.files?.[0] || null)}
                />
              </div>

            </div>

            <div className="flex gap-4 mt-6">
              <button
                className="flex-1 bg-gray-300 py-2 rounded-md"
                onClick={() => setIsUploadModalOpen(false)}
              >
                Cancelar
              </button>
              <button
                className="flex-1 bg-teal-500 py-2 text-white rounded-md"
                onClick={handleUpload}
              >
                Adicionar
              </button>
            </div>

          </div>
        </div>
      )}

      {/* ========== MODAL VIEW/DETAILS ========== */}
      {isViewModalOpen && selectedRegulation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white p-8 rounded-lg w-full max-w-2xl">

            <div className="flex justify-between items-start mb-6">
              <h2 className="text-2xl font-bold">{selectedRegulation.title}</h2>
              <button
                onClick={() => setIsViewModalOpen(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">Modalidade</label>
                <p className="text-lg text-gray-900">{getModalityName(selectedRegulation.modality_id)}</p>
              </div>

              {selectedRegulation.description && (
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Descrição</label>
                  <p className="text-gray-900 whitespace-pre-wrap">{selectedRegulation.description}</p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">Data de Criação</label>
                <p className="text-gray-900">
                  {new Date(selectedRegulation.created_at).toLocaleDateString('pt-PT', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                  })}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">Ficheiro</label>
                <a
                  href={selectedRegulation.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  Descarregar Regulamento
                </a>
              </div>
            </div>

            <div className="flex gap-4 mt-8 pt-4 border-t">
              <button
                onClick={handleDelete}
                className="px-6 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
              >
                Eliminar
              </button>
              <button
                onClick={() => setIsViewModalOpen(false)}
                className="flex-1 px-6 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
              >
                Fechar
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};

export default Regulamentos;
