import { useState } from "react";
import { useModal } from "../../contexts/ModalContext";
import { useSeason } from "../../contexts/SeasonContext";
import HelpTooltip from "../HelpTooltip";
import { seasonsApi } from "../../api/seasons";
import { useNotification } from "../../contexts/NotificationProvider";
import Button from "../utils/Button";

const NewSeasonModal = () => {
    const { popModal } = useModal();
    const { activeSeason, refreshSeasons } = useSeason();
    const { notify } = useNotification();

    const [confirmationText, setConfirmationText] = useState("");
    const [newSeasonName, setNewSeasonName] = useState(`Época ${new Date().getFullYear()}/${new Date().getFullYear() + 1}`);
    const [isLoading, setIsLoading] = useState(false);

    const onClose = () => {
        popModal();
    };

    const handleFinishSeason = () => {
        if (confirmationText !== "FINALIZAR") {
            notify('Por favor, digite "FINALIZAR" para confirmar', "error");
            return;
        }
        if (newSeasonName.trim() === "") {
            notify("O nome da nova época não pode estar vazio.", "error");
            return;
        }
        setIsLoading(true);
        seasonsApi.createSeason({
            name: newSeasonName,
        }).then(() => {
            notify(`Época ${activeSeason?.name} finalizada com sucesso!`, "success");
            onClose();
            refreshSeasons();
        }).catch((error) => {
            console.error("Erro ao finalizar época:", error);
            notify("Ocorreu um erro ao finalizar a época. Por favor, tente novamente.", "error");
        }).finally(() => {
            setIsLoading(false);
        });
    };

    if (!activeSeason) return null;

    return (
      <div className="bg-white p-8 rounded-lg max-w-md w-full">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">
          Confirmar Finalização de Época
        </h2>
        <div className="mb-6 space-y-3">
          <p className="text-gray-700">
            Tem certeza que deseja{" "}
            <span className="font-bold text-red-600">
              finalizar a época {activeSeason.name}
            </span>
            ?
          </p>
          <div className="bg-red-50 border-l-4 border-red-500 p-4">
            <p className="text-sm text-red-800 font-semibold mb-2">
              ATENÇÃO - AÇÃO IRREVERSÍVEL:
            </p>
            <ul className="text-sm text-red-700 space-y-1 list-disc list-inside">
              <li>
                <strong>Esta ação NÃO pode ser revertida!</strong>
              </li>
              <li>
                A época será marcada como <strong>FINALIZADA</strong>
              </li>
              <li>Não será possível modificar jogos ou torneios desta época</li>
              <li>Os resultados serão permanentemente arquivados</li>
              <li>Verifique que todos os jogos foram concluídos</li>
            </ul>
          </div>
          <p className="text-gray-700">
            Para iniciar uma nova época, insira o nome da próxima época abaixo:
          </p>
          <input
            type="text"
            className="border border-gray-300 rounded-md px-4 py-2 w-full"
            placeholder="Nome da nova época (ex: Época 2024/2025)"
            value={newSeasonName}
            onChange={(e) => setNewSeasonName(e.target.value)}
          />
          <p className="text-sm text-gray-600 italic mt-4 flex items-center gap-1">
            Digite "FINALIZAR" para confirmar:
            <HelpTooltip
              text="Esta confirmação é obrigatória pois a ação é irreversível. Todos os resultados e dados da época serão arquivados permanentemente e não poderão ser modificados."
              position="right"
            />
          </p>
          <input
            type="text"
            className="border border-gray-300 rounded-md px-4 py-2 w-full"
            placeholder="Digite FINALIZAR"
            id="confirm-finish-input"
            value={confirmationText}
            onChange={(e) => setConfirmationText(e.target.value)}
          />
        </div>
        <div className="flex gap-4">
          <Button onClick={onClose} type="secondary" flexible={true}>
            Cancelar
          </Button>
          <Button
            onClick={handleFinishSeason}
            type="danger"
            flexible={true}
            disabled={isLoading || confirmationText !== "FINALIZAR"}
          >
            {isLoading ? "A finalizar..." : "Finalizar Época"}
          </Button>
        </div>
      </div>
    );
};

export default NewSeasonModal;
