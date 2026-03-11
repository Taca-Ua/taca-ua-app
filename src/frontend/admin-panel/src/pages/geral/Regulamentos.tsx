import React, { useState, useEffect } from "react";
import ConfirmModal from "../../components/ConfirmModal";
import Sidebar from "../../components/geral_navbar";
import { regulationsApi, type Regulation, type RegulationCreate } from '../../api/regulations';
import { modalitiesApi, type Modality } from '../../api/modalities';
import { useNotification } from '../../contexts/NotificationProvider';

const Regulamentos: React.FC = () => {
  const [regulations, setRegulations] = useState<Regulation[]>([]);
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();
  const [searchTerm, setSearchTerm] = useState("");
  const [filterModality, setFilterModality] = useState("");
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedRegulation, setSelectedRegulation] = useState<Regulation | null>(null);
  const [deletingRegulation, setDeletingRegulation] = useState(false);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const checkFileExists = async (url: string) => {
    try {
      const response = await fetch(url, { method: 'HEAD' });
      return response.ok;
    } catch (err) {
      return false;
    }
  };

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

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const [regulationsData, modalitiesData] = await Promise.all([
        regulationsApi.getAll(),
        modalitiesApi.getAll(),
      ]);

      console.log("ESTRUTURA DO REGULAMENTO:", regulationsData[0]);

      const existingRegulations = await Promise.all(
        regulationsData.map(async (reg) => {
          const exists = await checkFileExists(reg.file_url);
          return exists ? reg : null;
        })
      );

      setRegulations(existingRegulations.filter((r): r is Regulation => r !== null));
      setModalities(modalitiesData);
    } catch (err) {
      console.error('Failed to fetch data:', err);
      notify('Não foi possível carregar os regulamentos. Tente recarregar a página.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const filteredRegulations = regulations.filter(r =>
    r.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !file) {
      notify('Título e ficheiro são obrigatórios', 'error');
      return;
    }

    try {
      setUploading(true);
      // O setError(''); foi removido pois já não usamos esse estado

      // Chamada à API usando os teus dados
      const newRegulation = await regulationsApi.create({
        title,
        file,
        description: description || undefined,
      });

      // Atualiza a lista local com o que veio do servidor
      setRegulations(prev => [newRegulation, ...prev]);

      // Limpa o formulário e fecha o modal
      setTitle("");
      setDescription("");
      setFile(null);
      setIsUploadModalOpen(false);
      
      notify("Regulamento adicionado com sucesso!", "success");
    } catch (err: unknown) {
      console.error('Upload failed:', err);
      if (err instanceof Error) {
        notify(err.message, 'error');
      } else {
        notify('Não foi possível processar o upload do ficheiro.', 'error');
      }
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedRegulation) return;
    
    // Em vez do confirm do browser, abre o modal customizado da dev
    setIsDeleteModalOpen(true);
  };

  const confirmDelete = async () => {
    if (!selectedRegulation) return;

    try {
      setDeletingRegulation(true);
      
      // Chamada à tua API
      await regulationsApi.delete(selectedRegulation.id);
      
      // Atualiza a lista local
      setRegulations(prev => prev.filter(r => r.id !== selectedRegulation.id));
      
      // Fecha ambos os modais (o de visualização e o de confirmação)
      setIsDeleteModalOpen(false);
      setIsViewModalOpen(false);
      setSelectedRegulation(null);
      
      // Notificação de sucesso da dev
      notify('Regulamento eliminado com sucesso!', 'success');
      
    } catch (err: unknown) {
      console.error('Failed to delete regulation:', err);
      
      // Tratamento de erro padronizado
      if (err instanceof Error) {
        notify(err.message, 'error');
      } else {
        notify('Não foi possível eliminar o regulamento. Tente novamente.', 'error');
      }
    } finally {
      setDeletingRegulation(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          
          {/* Header estilizado da HEAD */}
          <header className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Gestão de Regulamentos</h1>
              <p className="text-gray-500 mt-1">Consulte e gira os documentos oficiais do sistema.</p>
            </div>

            <button
              onClick={() => setIsUploadModalOpen(true)}
              className="px-6 py-3 bg-teal-600 text-white font-semibold rounded-lg hover:bg-teal-700 transition-shadow shadow-md"
            >
              + Novo Regulamento
            </button>
          </header>

          {/* Barra de Ferramentas: Teu Search + Filtro de Modalidade da dev */}
          <div className="bg-white p-4 rounded-lg shadow-sm mb-6 border border-gray-200 flex flex-wrap gap-6 items-end">
            <div className="relative max-w-md flex-1">
              <label className="block mb-1 text-xs font-bold text-gray-400 uppercase tracking-widest">Pesquisar</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </span>
                <input
                  type="text"
                  placeholder="Por título..."
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white focus:outline-none focus:ring-1 focus:ring-teal-500 sm:text-sm"
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            <div className="min-w-[200px]">
              <label className="block mb-1 text-xs font-bold text-gray-400 uppercase tracking-widest">Modalidade</label>
              <select
                className="block w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-sm focus:outline-none focus:ring-1 focus:ring-teal-500"
                value={filterModality}
                onChange={e => setFilterModality(e.target.value)}
              >
                <option value="">Todas as Modalidades</option>
                {modalities.map(m => (
                  <option key={m.id} value={m.id}>{m.name}</option>
                ))}
              </select>
            </div>
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
                    onClick={() => { setSelectedRegulation(reg); setIsViewModalOpen(true); }}
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
      </main>

      {isUploadModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in duration-200">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-800">Novo Regulamento</h2>
              <button onClick={() => setIsUploadModalOpen(false)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>

            <form onSubmit={handleUpload} className="p-6 space-y-5">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Título do Documento *</label>
                <input
                  required
                  className="w-full border border-gray-300 px-4 py-2 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none"
                  value={title}
                  onChange={e => setTitle(e.target.value)}
                  placeholder="Ex: Regulamento de Basquetebol 2026"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Descrição Breve</label>
                <textarea
                  className="w-full border border-gray-300 px-4 py-2 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none min-h-[100px]"
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  placeholder="Opcional: detalhes sobre as regras ou atualizações..."
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Ficheiro (Apenas PDF) *</label>
                <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-teal-400 transition-colors">
                  <div className="space-y-1 text-center">
                    <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                      <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <div className="flex text-sm text-gray-600">
                      <label className="relative cursor-pointer bg-white rounded-md font-medium text-teal-600 hover:text-teal-500 focus-within:outline-none">
                        <span>Carregar ficheiro</span>
                        <input 
                          type="file" 
                          accept="application/pdf" 
                          className="sr-only" 
                          onChange={e => setFile(e.target.files?.[0] || null)}
                          required
                        />
                      </label>
                    </div>
                    <p className="text-xs text-gray-500">{file ? file.name : "PDF até 10MB"}</p>
                  </div>
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-colors"
                  onClick={() => setIsUploadModalOpen(false)}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="flex-1 px-4 py-2 bg-teal-600 text-white font-semibold rounded-lg hover:bg-teal-700 shadow-lg disabled:bg-gray-400 transition-all"
                >
                  {uploading ? "A enviar..." : "Guardar Regulamento"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {isViewModalOpen && selectedRegulation && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden animate-in slide-in-from-bottom-4 duration-300">
            
            <div className="p-8">
              <div className="flex justify-between items-start">
                <h2 className="text-2xl font-bold text-gray-900">{selectedRegulation.title}</h2>
                <button onClick={() => setIsViewModalOpen(false)} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
              </div>

              <div className="mt-8 space-y-6">
                <div className="grid grid-cols-2 gap-8">
                   <div>
                    <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest">Data de Submissão</label>
                    <p className="mt-1 text-gray-900 font-medium">
                      {formatDisplayDate(selectedRegulation.created_at)}
                    </p>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest">Tipo de Ficheiro</label>
                    <p className="mt-1 text-gray-900 font-medium">Documento PDF</p>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest">Descrição</label>
                  <p className="mt-2 text-gray-700 bg-gray-50 p-4 rounded-lg italic border-l-4 border-gray-200">
                    {selectedRegulation.description || "Nenhuma descrição adicional para este documento."}
                  </p>
                </div>

                <div className="p-4 bg-blue-50 rounded-xl flex items-center justify-between border border-blue-100">
                  <div className="flex items-center gap-3">
                    <div className="bg-blue-500 p-2 rounded-lg text-white">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                    </div>
                    <div>
                      <p className="text-sm font-bold text-blue-900">Aceder ao Ficheiro</p>
                      <p className="text-xs text-blue-700">O documento será aberto num novo separador.</p>
                    </div>
                  </div>
                  <a
                    href={selectedRegulation.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 bg-blue-600 text-white text-sm font-bold rounded-lg hover:bg-blue-700 transition-all shadow-sm"
                  >
                    Visualizar
                  </a>
                </div>
              </div>

              <div className="mt-10 pt-6 border-t border-gray-100 flex gap-4">
                <button
                  onClick={handleDelete}
                  className="px-6 py-2.5 text-sm font-bold bg-white text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
                >
                  Eliminar Documento
                </button>
                <button
                  onClick={() => setIsViewModalOpen(false)}
                  className="flex-1 px-6 py-2.5 text-sm font-bold bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors"
                >
                  Fechar Painel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <ConfirmModal
        isOpen={isDeleteModalOpen}
        title="Eliminar regulamento"
        message={selectedRegulation ? `Tem certeza que deseja eliminar "${selectedRegulation.title}"?` : ''}
        confirmLabel="Eliminar"
        variant="danger"
        loading={deletingRegulation}
        onCancel={() => {
          if (!deletingRegulation) {
            setIsDeleteModalOpen(false);
          }
        }}
        onConfirm={confirmDelete}
      />

    </div>
  );
};

export default Regulamentos;