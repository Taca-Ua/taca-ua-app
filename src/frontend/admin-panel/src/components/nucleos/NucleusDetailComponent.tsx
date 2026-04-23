import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useNotification } from "../../contexts/NotificationProvider";
import { type NucleoDetail, nucleosApi } from "../../api/nucleos";
import HelpTooltip from "../HelpTooltip";
import NucleusEditModal from "./NucleusEditModal";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";

const NucleusDetailComponent = ( { nucleusId } : { nucleusId: string }) => {
  const { notify } = useNotification();
  const navigate = useNavigate();

  const [nucleus, setNucleus] = useState<NucleoDetail | null>(null);
  const { pushModal } = useModal();

  useEffect(() => {
    // Fetch nucleus details from API
    const fetchNucleus = async () => {
      try {
        const nucleusData = await nucleosApi.getById(nucleusId);
        setNucleus(nucleusData);
      } catch (error) {
        console.error("Error fetching nucleus details:", error);
      }
    };

    fetchNucleus();
  }, [nucleusId]);

  const handleDelete = async () => {
    try {
      await nucleosApi.delete(String(nucleusId));
      navigate('/nucleos');
    } catch (err) {
      console.error('Failed to delete course:', err);
      notify('Não foi possível eliminar o núcleo. Poderá ter cursos ou membros associados.', 'error');
    }
  };

  if (!nucleus) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-500">Carregando detalhes do núcleo...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      <div>
        <label className="block text-teal-500 font-medium mb-2">Logo</label>
        <div className="flex items-center gap-4">
          <div className="w-24 h-24 rounded-full bg-white flex items-center justify-center overflow-hidden border-2 border-teal-500">
            <span className="text-teal-600 font-bold text-2xl">
              {nucleus.abbreviation}
            </span>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-teal-500 font-medium mb-2">
          Abreviatura{" "}
          <HelpTooltip
            text="Sigla ou código curto do núcleo, ex: NEECT, NEEEC. Utilizado como identificador visual no sistema."
            className="ml-1"
          />
        </label>
        <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
          {nucleus.abbreviation}
        </div>
      </div>

      <div>
        <label className="block text-teal-500 font-medium mb-2">Nome</label>
        <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
          {nucleus.name}
        </div>
      </div>

      {nucleus.courses.length > 0 && (
        <div>
          <label className="block text-teal-500 font-medium mb-2">
            Cursos Associados
          </label>
          <div className="bg-gray-100 px-4 py-3 rounded-md">
            <div className="flex flex-wrap gap-2">
              {[...nucleus.courses]
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((course) => (
                  <span
                    key={course.id}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 font-medium"
                  >
                    {course.name}
                    <span className="ml-1 text-blue-600">
                      ({course.abbreviation})
                    </span>
                  </span>
                ))}
            </div>
          </div>
        </div>
      )}

      <div className="flex gap-4 pt-4">
        <Button
          onClick={() => pushModal(
            <NucleusEditModal
              nucleusState={[nucleus, setNucleus]}
            />
          )}
          type="primary"
          flexible={true}
        >
          Editar
        </Button>
        <Button
          onClick={handleDelete}
          type="danger"
          confirmation={{
            title: "Eliminar núcleo",
            message: `Tem certeza que deseja eliminar "${nucleus.name}"?`,
            confirmLabel: "Eliminar",
          }}
          flexible={true}
        >
          Eliminar
        </Button>
      </div>
    </div>
  );
};

export default NucleusDetailComponent;
