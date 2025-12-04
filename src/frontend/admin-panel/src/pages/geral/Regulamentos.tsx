import { useState } from "react";
import { useNavigate } from 'react-router-dom';
import Sidebar from "../../components/geral_navbar";


interface Regulation {
    id: number;
    title: string;
    file_url: string;
    modality_id?: number;
    description?: string;
  }

const mockRegulations: Regulation[] = [
    {
      id: 1,
      title: "Regulamento Futebol 25/26",
      file_url: "/files/reg_futebol_25_26.pdf",
      modality_id: 1,
      description: "Regulamento oficial de futebol",
    },
    {
      id: 2,
      title: "Regulamento Basquete Elite",
      file_url: "/files/reg_basket_elite_2025.pdf",
      modality_id: 2,
      description: "Versão atualizada",
    },
  ];


const Regulamentos = () => {
  const navigate = useNavigate();
  const [regulations, setRegulations] = useState<Regulation[]>(mockRegulations);
  const [filterModality, setFilterModality] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Campos Upload
  const [title, setTitle] = useState("");
  const [modalityId, setModalityId] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const filtered = regulations.filter(r =>
    (!filterModality || String(r.modality_id) === filterModality)
  );

  const handleUpload = () => {
    if (!title.trim() || !file) {
      alert("Título e ficheiro são obrigatórios");
      return;
    }

    const newRegulation: Regulation = {
      id: regulations.length + 1,
      title,
      file_url: URL.createObjectURL(file), // mock
      modality_id: modalityId ? Number(modalityId) : undefined,
      description: description || undefined,
    };

    setRegulations([...regulations, newRegulation]);

    // reset
    setTitle("");
    setModalityId("");
    setDescription("");
    setFile(null);
    setIsModalOpen(false);
  };

  const deleteRegulation = (id: number) => {
    if (!confirm("Eliminar regulamento?")) return;
    setRegulations(regulations.filter(r => r.id !== id));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8 max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Regulamentos</h1>

          <button
            onClick={() => setIsModalOpen(true)}
            className="px-6 py-3 bg-teal-500 text-white rounded-md hover:bg-teal-600"
          >
            + Adicionar Regulamento
          </button>
        </div>

        {/* Filtros */}
        <div className="flex gap-6 mb-6">
          <div>
            <label className="block mb-1 font-medium">Modalidade</label>
            <input
              type="number"
              className="border px-3 py-2 rounded-md"
              placeholder="ex: 1"
              value={filterModality}
              onChange={e => setFilterModality(e.target.value)}
            />
          </div>
        </div>

        {/* Lista */}
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          {filtered.length > 0 ? filtered.map(r => (
            <div
              key={r.id}
              className="p-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer flex justify-between"
              onClick={() => navigate(`/geral/regulamentos/${r.id}`)}
            >
              <div className="font-medium">{r.title}</div>
              <div className="text-gray-600 text-sm">
                Modalidade {r.modality_id ?? "—"}
              </div>
            </div>
          )) : (
            <p className="text-gray-500 text-center">Nenhum regulamento encontrado.</p>
          )}
        </div>

      </div>

      {/* ========== MODAL UPLOAD ========== */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
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
                <input
                  type="number"
                  className="border px-3 py-2 rounded-md w-full"
                  value={modalityId}
                  onChange={e => setModalityId(e.target.value)}
                />
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
                onClick={() => setIsModalOpen(false)}
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

    </div>
  );
};

export default Regulamentos;
