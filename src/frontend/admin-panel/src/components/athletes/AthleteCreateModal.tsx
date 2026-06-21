import { useState } from "react"
import { type AthleteListItem, athletesApi } from "../../api/athletes"
import HelpTooltip from "../HelpTooltip"
import { coursesApi } from "../../api/courses"
import ChoseOneInput from "../utils/inputs/ChoseOneInput"
import Button from "../utils/Button"
import { useNotification } from "../../contexts/NotificationProvider"
import { useModal } from "../../contexts/ModalContext"

const AthleteCreateModal = ( {
    onCreate
} : {
    onCreate?: (newAthlete: AthleteListItem) => void
} ) => {
    const { notify } = useNotification();
    const { popModal } = useModal();

    const [memberName, setMemberName] = useState("")
    const [studentNumber, setStudentNumber] = useState("")
    const [courseId, setCourseId] = useState("")

    const onClose = () => {
        popModal();
        setMemberName("");
        setCourseId("");
        setStudentNumber("");
    }

    const handleAddMember = () => {
        const trimmedStudentNumber = studentNumber.trim();

        if (!trimmedStudentNumber) {
            notify('Por favor, preencha o número de estudante.', 'error');
            return;
        }

        if (!/^\d+$/.test(trimmedStudentNumber)) {
            notify('O número de estudante (NMEC) deve conter apenas dígitos.', 'error');
            return;
        }

        if (trimmedStudentNumber.length > 13) {
            notify('O número de estudante (NMEC) não pode ter mais de 13 caracteres.', 'error');
            return;
        }

        if (!courseId.trim()) {
            notify('Por favor, preencha o curso.', 'error');
            return;
        }

        athletesApi.create({
            name: memberName,
            course_id: String(courseId),
            student_number: trimmedStudentNumber,
            is_member: true,
        }).then((newParticipant) => {
            if (onCreate) onCreate(newParticipant);
            notify('Atleta criado com sucesso!', 'success');
            onClose();
        }).catch((err) => {
            console.error("Failed to create athlete:", err);
            notify('Erro ao criar atleta. Tente novamente.', 'error');
        });
    }

    return (
        <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
          <h2 className="text-2xl font-bold mb-6 text-gray-800">
            Adicionar Membro
          </h2>

          <div className="space-y-4">
            <div>
              <label
                htmlFor="memberName"
                className="block text-gray-700 font-medium mb-2"
              >
                Nome <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="memberName"
                value={memberName}
                onChange={(e) => setMemberName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Digite o nome do membro"
              />
            </div>

            <div>
              <label
                htmlFor="studentNumber"
                className="block text-gray-700 font-medium mb-2"
              >
                Número de Estudante{" "}
                <HelpTooltip
                  text="Número mecanológráfico (NMEC) do estudante na Universidade de Aveiro. Utilizado para verificação de elegibilidade."
                  className="ml-1"
                />{" "}
                <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="studentNumber"
                value={studentNumber}
                onChange={(e) => setStudentNumber(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Digite o NMEC (ex: 12345)"
              />
            </div>

            <div>
              <label
                htmlFor="courseId"
                className="block text-gray-700 font-medium mb-2"
              >
                Curso{" "}
                <HelpTooltip
                  text="Curso académico do estudante na Universidade de Aveiro. Utilizado para organização e filtros de equipas."
                  className="ml-1"
                />{" "}
                <span className="text-red-500">*</span>
              </label>
              <ChoseOneInput
                allElementsLoader={() =>
                  coursesApi
                    .getAll()
                    .then((courses) =>
                      courses.map((course) => ({
                        id: course.id,
                        title: course.abbreviation,
                        subTitle: course.name,
                      })),
                    )
                }
                onSelect={(element) => {
                  setCourseId(element ? element.id : "");
                }}
              />
            </div>
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
                onClick={handleAddMember}
                type="primary"
                flexible={true}
            >
                Adicionar
            </Button>
          </div>
        </div>
    );
}

export default AthleteCreateModal
