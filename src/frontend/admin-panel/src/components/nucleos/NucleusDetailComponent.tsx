import { useEffect, useState } from "react";
import { useNotification } from "../../contexts/NotificationProvider";
import { type NucleoDetail, nucleosApi } from "../../api/nucleos";
import NucleusEditModal from "./NucleusEditModal";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";
import { useAuth } from "../../hooks/useAuth";
import LazyImage from "../utils/LazyImage";
import { useSeason } from "../../contexts/SeasonContext";
import type { ApiError } from "../../api/client";

const NucleusDetailComponent = ( {
  nucleusId,
  nucleusState
} : {
  nucleusId: string,
  nucleusState?: [NucleoDetail | null, React.Dispatch<React.SetStateAction<NucleoDetail | null>>]
}) => {
  const { notify } = useNotification();
  const { isAdminGeneral } = useAuth();
  const { loadedSeason } = useSeason();

  const [nucleus, setNucleus] = nucleusState || useState<NucleoDetail | null>(null);
  const [logoUrl, setLogoUrl] = useState<string | null>(null);
  const { pushModal } = useModal();

  useEffect(() => {
    nucleosApi.getById(nucleusId, loadedSeason?.id)
      .then(nucleusData => {
        setNucleus(nucleusData);

        if (nucleusData.logo_url) { // Add cache-busting query parameter to logo URL to force refresh
          setLogoUrl(`${nucleusData.logo_url}?t=${Date.now()}`);
        }
      })
      .catch(error => {
        console.error("Error fetching nucleus details:", error);
        notify("Não foi possível carregar os detalhes do núcleo.", "error");
      });
  }, [nucleusId, loadedSeason?.id]);

  // Update logoUrl when nucleus.logo_url changes (e.g., after editing)
  useEffect(() => {
    if (nucleus?.logo_url) {
      setLogoUrl(`${nucleus.logo_url}?t=${Date.now()}`);
    } else {
      setLogoUrl(null);
    }
  }, [nucleus?.logo_url]);

  const handleAddToSeason = () => {
    if (!nucleus) return;
    if (!loadedSeason) {
      notify('Não foi possível adicionar o núcleo à época. Nenhuma época carregada.', 'error');
      return;
    }

    nucleosApi.addToSeason(nucleus.id, loadedSeason.id)
      .then(updatedNucleus => {
        setNucleus(updatedNucleus);
        notify(`Núcleo "${updatedNucleus.name}" adicionado à época com sucesso.`, 'success');
      })
      .catch((err: ApiError) => {
        console.error('Failed to add nucleus to season:', err);
        notify('Não foi possível adicionar o núcleo à época.\n'+ err.message, 'error');
      });
  }

  const handleRemoveFromSeason = () => {
    if (!nucleus) return;
    if (!loadedSeason) {
      notify('Não foi possível remover o núcleo da época. Nenhuma época carregada.', 'error');
      return;
    }
    nucleosApi.removeFromSeason(nucleus.id, loadedSeason.id)
      .then(updatedNucleus => {
        setNucleus(updatedNucleus);
        notify(`Núcleo "${updatedNucleus.name}" removido da época com sucesso.`, 'success');
      })
      .catch((err: ApiError) => {
        console.error('Failed to remove nucleus from season:', err);
        notify('Não foi possível remover o núcleo da época.\n'+ err.message, 'error');
      });
  }

  if (!nucleus) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-500">Carregando detalhes do núcleo...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-x-4 space-y-4 flex flex-col md:flex-row">
      <div>
        { logoUrl ? (
          <div className="w-24 h-24 flex items-center justify-center overflow-hidden">
            <LazyImage src={logoUrl} alt={`${nucleus?.name} logo`} className="w-full h-full object-cover" />
          </div>
        ) : (
          <div className="flex items-center gap-4">
            <div className="w-24 h-24 rounded-full bg-white flex items-center justify-center overflow-hidden border-2 border-teal-500">
              <span className="text-teal-600 font-bold text-2xl">
                {nucleus?.abbreviation}
              </span>
            </div>
          </div>
        )}
      </div>

      <div className="flex flex-col gap-1 flex-grow">
        <h1 className="text-2xl font-bold text-gray-800">
          <span className="text-teal-500 font-medium text-lg">Nome:</span> {nucleus.name}
        </h1>
        <h2 className="text-lg font-semibold text-gray-700 mb-1">
          <span className="text-teal-500 font-medium text-lg">Abreviação:</span> {nucleus.abbreviation}
        </h2>
      </div>

      <div className="flex flex-row gap-2 flex-grow md:flex-col">
        <Button
          onClick={() =>
            pushModal(<NucleusEditModal nucleusState={[nucleus, setNucleus]} />)
          }
          type="primary"
          flexible={true}
          active={isAdminGeneral}
        >
          Editar
        </Button>
        { (nucleus.belongs_to_season !== undefined) && (
          <div className="flex">
            <Button
              onClick={handleAddToSeason}
              type="primary"
              flexible={true}
              active={isAdminGeneral && loadedSeason !== null && !nucleus.belongs_to_season}
            >
              + Adicionar à época
            </Button>
            <Button
              onClick={handleRemoveFromSeason}
              type="danger"
              flexible={true}
              active={isAdminGeneral && loadedSeason !== null && nucleus.belongs_to_season}
            >
              - Remover da época
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default NucleusDetailComponent;
