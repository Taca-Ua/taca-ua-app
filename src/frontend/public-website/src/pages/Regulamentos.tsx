import { useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import RegulamentoCard from '../components/RegulamentoCard';

interface Regulamento {
  id: string;
  title: string;
  category: string;
  epoca: string;
  description: string;
  pdfUrl: string;
}

function Regulamentos() {
  const [selectedEpoca, setSelectedEpoca] = useState('2025/2026');
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedRegulamento, setSelectedRegulamento] = useState<Regulamento | null>(null);
  const [pdfExists, setPdfExists] = useState(false);
  const [checkingPdf, setCheckingPdf] = useState(true);

  // Mock data - replace with API call later
  const allRegulamentos: Regulamento[] = [
    {
      id: '1',
      title: 'Geral',
      category: 'Regulamento',
      epoca: '2025/2026',
      description: 'Regulamento geral da Taça UA para a época 2025/2026. Define as regras gerais, pontuação, e normas de conduta para todas as modalidades.',
      pdfUrl: '/regulamentos/geral-2025-2026.pdf',
    },
    {
      id: '2',
      title: 'Futsal',
      category: 'Regulamento',
      epoca: '2025/2026',
      description: 'Regulamento específico para a modalidade de Futsal. Inclui regras de jogo, composição de equipas, e critérios de desempate.',
      pdfUrl: '/regulamentos/futsal-2025-2026.pdf',
    },
    {
      id: '3',
      title: 'Andebol',
      category: 'Regulamento',
      epoca: '2025/2026',
      description: 'Regulamento específico para a modalidade de Andebol. Define as normas de participação e competição.',
      pdfUrl: '/regulamentos/andebol-2025-2026.pdf',
    },
    {
      id: '4',
      title: 'Minecraft',
      category: 'Regulamento',
      epoca: '2025/2026',
      description: 'Regulamento específico para o torneio de Minecraft. Define as regras do jogo, mapas permitidos, e critérios de vitória.',
      pdfUrl: '/regulamentos/minecraft-2025-2026.pdf',
    },
  ];

  const filteredRegulamentos = allRegulamentos.filter((reg) => {
    const matchesEpoca = reg.epoca === selectedEpoca;
    const matchesSearch = reg.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          reg.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesEpoca && matchesSearch;
  });

  const handleCardClick = (id: string) => {
    const regulamento = allRegulamentos.find(reg => reg.id === id);
    if (!regulamento) return;

    setSelectedRegulamento(regulamento);
    setShowModal(true);
    setCheckingPdf(true);

    fetch(regulamento.pdfUrl)
      .then((response) => {
        const contentType = response.headers.get('content-type');
        const isPdf = contentType?.includes('pdf') || contentType?.includes('application/pdf');
        setPdfExists(response.ok && response.status === 200 && !!isPdf);
        setCheckingPdf(false);
      })
      .catch(() => {
        setPdfExists(false);
        setCheckingPdf(false);
      });
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedRegulamento(null);
    setPdfExists(false);
    setCheckingPdf(true);
  };

  const handleDownload = () => {
    if (selectedRegulamento && pdfExists) {
      window.open(selectedRegulamento.pdfUrl, '_blank');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      
      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold mb-8 text-gray-800">
            Regulamentos
          </h1>

          {/* Filters */}
          <div className="flex flex-col md:flex-row gap-4 mb-8">
            {/* Search */}
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Procurar Regulamento
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Procurar..."
                  className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
                />
                <svg
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
            </div>

            {/* Época Filter */}
            <div className="md:w-64">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Época
              </label>
              <select
                value={selectedEpoca}
                onChange={(e) => setSelectedEpoca(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
              >
                <option value="2025/2026">25/26</option>
                <option value="2024/2025">24/25</option>
                <option value="2023/2024">23/24</option>
              </select>
            </div>
          </div>

          {/* Regulamentos Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {filteredRegulamentos.length > 0 ? (
              filteredRegulamentos.map((regulamento) => (
                <RegulamentoCard
                  key={regulamento.id}
                  title={regulamento.title}
                  category={regulamento.category}
                  epoca={regulamento.epoca}
                  onClick={() => handleCardClick(regulamento.id)}
                />
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <p className="text-xl text-gray-500">
                  Nenhum regulamento encontrado.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />

      {/* PDF Download Modal */}
      {showModal && selectedRegulamento && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fadeIn">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl flex flex-col animate-slideUp">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div>
                <h2 className="text-2xl font-bold text-gray-800">
                  {selectedRegulamento.title}
                </h2>
                <p className="text-sm text-gray-600">
                  {selectedRegulamento.category} • {selectedRegulamento.epoca}
                </p>
              </div>
              <button
                onClick={handleCloseModal}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-hidden p-8">
              <div className="h-full flex items-center justify-center">
                <div className="text-center max-w-2xl">
                  {checkingPdf ? (
                    <>
                      <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-teal-600 mx-auto mb-6"></div>
                      <p className="text-gray-600 text-lg">A verificar disponibilidade...</p>
                    </>
                  ) : pdfExists ? (
                    <>
                      <div className="w-24 h-24 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-6">
                        <svg className="w-14 h-14 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <h3 className="text-3xl font-bold text-gray-800 mb-4">Regulamento Disponível</h3>
                      <p className="text-gray-600 text-lg mb-2">
                        {selectedRegulamento.description}
                      </p>
                      <p className="text-gray-500 text-sm">
                        Clique no botão "Download" abaixo para visualizar o regulamento.
                      </p>
                    </>
                  ) : (
                    <>
                      <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                        <svg className="w-14 h-14 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </div>
                      <h3 className="text-3xl font-bold text-gray-800 mb-4">PDF Não Encontrado</h3>
                      <p className="text-gray-600 text-lg">
                        Este regulamento ainda não está disponível. Por favor, tente novamente mais tarde.
                      </p>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={handleCloseModal}
                className="px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors font-semibold text-gray-700"
              >
                Fechar
              </button>
              <button
                onClick={handleDownload}
                disabled={!pdfExists || checkingPdf}
                className={`px-6 py-2 rounded-md font-semibold flex items-center gap-2 transition-colors ${
                  pdfExists && !checkingPdf
                    ? 'bg-teal-600 text-white hover:bg-teal-700 cursor-pointer'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Regulamentos;
