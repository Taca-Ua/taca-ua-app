import { useParams, useNavigate } from "react-router-dom";
import { useMemo, useState } from "react";
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

const RegulamentoDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const initial = useMemo(
    () => mockRegulations.find(r => r.id === Number(id)) || null,
    [id]
  );

  const [regulation, setRegulation] = useState<Regulation | null>(initial);
  const [isEditModal, setIsEditModal] = useState(false);

  // Campos edição
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editModality, setEditModality] = useState("");

  if (!regulation) {
    return (
      <div className="p-10 text-red-600 text-center">
        Regulamento não encontrado.
      </div>
    );
  }

  const openEdit = () => {
    setEditTitle(regulation.title);
    setEditDescription(regulation.description ?? "");
    setEditModality(regulation.modality_id?.toString() ?? "");
    setIsEditModal(true);
  };

  const saveEdit = () => {
    setRegulation({
      ...regulation,
      title: editTitle,
      description: editDescription || undefined,
      modality_id: editModality ? Number(editModality) : undefined,
    });
    setIsEditModal(false);
  };

  const deleteRegulation = () => {
    if (!confirm("Eliminar este regulamento?")) return;
    navigate("/geral/regulamentos");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8 max-w-6xl mx-auto">

        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Detalhes do Regulamento</h1>

          <button
            onClick={deleteRegulation}
            className="bg-red-500 text-white px-6 py-2 rounded-md hover:bg-red-600"
          >
            Eliminar
          </button>
        </div>

        {/* Caixa principal */}
        <div className="grid grid-cols-2 gap-8">

          {/* Dados */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Informações</h2>

            <div className="space-y-4">

              <div>
                <label className="font-medium text-teal-600">Título</label>
                <div className="bg-gray-100 rounded-md p-3">
                  {regulation.title}
                </div>
              </div>

              <div>
                <label className="font-medium text-teal-600">Modalidade</label>
                <div className="bg-gray-100 rounded-md p-3">
                  {regulation.modality_id ?? "Nenhuma"}
                </div>
              </div>

              <div>
                <label className="font-medium text-teal-600">Descrição</label>
                <div className="bg-gray-100 rounded-md p-3 whitespace-pre-wrap">
                  {regulation.description ?? "—"}
                </div>
              </div>

              <div>
                <label className="font-medium text-teal-600">Ficheiro</label>
                <a
                  href={regulation.file_url}
                  target="_blank"
                  className="text-blue-600 underline block mt-2"
                >
                  Abrir ficheiro
                </a>
              </div>

              <div className="pt-4">
                <button
                  onClick={openEdit}
                  className="w-full bg-teal-500 hover:bg-teal-600 text-white py-2 rounded-md"
                >
                  Editar
                </button>
              </div>

            </div>
          </div>

          {/* Área vazia o futura */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Preview</h2>

            <p className="text-gray-500">
              (Opcional: preview pdf)
            </p>
          </div>

        </div>

      </div>

      {/* ========== MODAL Edition ========== */}
      {isEditModal && (
        <div className="fixed inset-0 bg-black/50 flex justify-center items-center">
          <div className="bg-white p-8 rounded-lg w-full max-w-md">

            <h2 className="text-2xl font-bold mb-6">Editar Regulamento</h2>

            <div className="space-y-4">

              <div>
                <label className="font-medium">Título</label>
                <input
                  className="border w-full px-4 py-2 rounded-md"
                  value={editTitle}
                  onChange={e => setEditTitle(e.target.value)}
                />
              </div>

              <div>
                <label className="font-medium">Descrição</label>
                <textarea
                  className="border w-full px-4 py-2 rounded-md min-h-[70px]"
                  value={editDescription}
                  onChange={e => setEditDescription(e.target.value)}
                />
              </div>

              <div>
                <label className="font-medium">Modalidade</label>
                <input
                  type="number"
                  className="border w-full px-4 py-2 rounded-md"
                  value={editModality}
                  onChange={e => setEditModality(e.target.value)}
                />
              </div>

            </div>

            <div className="flex gap-4 mt-6">
              <button
                className="flex-1 bg-gray-300 py-2 rounded-md"
                onClick={() => setIsEditModal(false)}
              >
                Cancelar
              </button>

              <button
                className="flex-1 bg-teal-500 py-2 text-white rounded-md"
                onClick={saveEdit}
              >
                Guardar
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};

export default RegulamentoDetails;
