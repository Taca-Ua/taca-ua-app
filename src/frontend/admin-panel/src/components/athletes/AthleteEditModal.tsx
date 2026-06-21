import { useEffect, useState } from "react";
import { type AthleteDetail, athletesApi } from "../../api/athletes"
import Button from "../utils/Button";
import HelpTooltip from "../HelpTooltip";
import DefinedStatesMenuComponent from "../utils/costum_menus/DefinedStatesMenuComponent";
import { useNotification } from "../../contexts/NotificationProvider";
import { useModal } from "../../contexts/ModalContext";
import { useAuth } from "../../hooks/useAuth";
import ChoseOneInput from "../utils/inputs/ChoseOneInput";
import { coursesApi } from "../../api/courses";

const AthleteEditModal = ( {
    athleteState,
    onSave,
} : {
    athleteState: [AthleteDetail, React.Dispatch<React.SetStateAction<AthleteDetail | null>>]
    onSave?: (updated: AthleteDetail) => void
  } ) => {
    const [athlete, setAthlete] = athleteState;
    const { notify } = useNotification();
    const { popModal } = useModal();
    const { isAdminGeneral } = useAuth();

    const [editedName, setEditedName] = useState(athlete.name);
    const [editedIsMember, setEditedIsMember] = useState(athlete.is_member);
    const [editedCourseId, setEditedCourseId] = useState<string | null>(athlete.course.id);

    useEffect(() => {
        setEditedName(athlete.name);
        setEditedIsMember(athlete.is_member);
        setEditedCourseId(athlete.course.id);
    }, [athlete]);

    const onClose = () => {
        popModal();
    }

    const handleSave = () => {
      if (!editedName.trim()) {
          alert("O nome do atleta não pode estar vazio.");
          return;
      }

      athletesApi.update(athlete.id, {
          name: editedName,
          is_member: editedIsMember,
          course_id: editedCourseId || undefined,
      }).then((updated) => {
          notify("Atleta atualizado com sucesso.", "success");
          setAthlete(updated);
          if (onSave) onSave(updated);
          onClose();
      }).catch((err) => {
          console.error("Failed to update athlete:", err);
          notify("Erro ao atualizar atleta. Tente novamente.", "error");
      });
    };

    return (
        <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
          <h2 className="text-2xl font-bold mb-6 text-gray-800">
            Editar Membro
          </h2>

          <div className="space-y-4">
            <div>
              <label
                htmlFor="editName"
                className="block text-gray-700 font-medium mb-2"
              >
                Nome <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="editName"
                value={editedName}
                onChange={(e) => setEditedName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Digite o nome do membro"
              />
            </div>

              <>
                <div>
                  <label className="block text-gray-700 font-medium mb-2">
                    Número de Estudante
                  </label>
                  <div className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-600">
                    {athlete.student_number}
                  </div>
                </div>

                {isAdminGeneral && (<div>
                  <label className="block text-gray-700 font-medium mb-2">
                    Tipo{" "}
                    <HelpTooltip
                      text="Membro: paga quota e tem acesso a todos os benefícios do núcleo. Não-Membro: pode participar mas com acesso limitado."
                      className="ml-1"
                    />
                  </label>
                  <DefinedStatesMenuComponent
                    states={[
                      { label: "Sócio", value: "member" },
                      { label: "Não Sócio", value: "non_member" },
                    ]}
                    onSelect={(value) => setEditedIsMember(value === "member")}
                    initialValue={editedIsMember ? "member" : "non_member"}
                  />
                </div>)}

                <div>
                  <label className="block text-gray-700 font-medium mb-2">
                    Curso
                  </label>
                  <ChoseOneInput
                    allElementsLoader={() => coursesApi.getAll().then(res => res.map(c => ({ id: c.id, title: c.name })))}
                    onSelect={(ele) => setEditedCourseId(ele? ele.id : null)}
                    initialElement={{ id: athlete.course.id, title: athlete.course.name }}
                  />
                </div>
              </>

          </div>

          <div className="flex gap-4 mt-6">
            <Button
                onClick={onClose}
                type="secondary"
                flexible={true}
            >
                Cancelar
            </Button>
            <Button
              onClick={handleSave}
              type="primary"
              flexible={true}
            >
              Guardar
            </Button>
          </div>
        </div>
    );
}

export default AthleteEditModal;
