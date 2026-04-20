import { useState } from "react";
import { type AdminDetail, administratorsApi } from "../../api/admins"
import HelpTooltip from "../HelpTooltip";
import AdminEditModal from "./AdminEditModal";
import AdminChangePasswordModal from "./AdminChangePasswordModal";
import { useAuth } from "../../hooks/useAuth";
import Button from "../utils/Button";
import { useNavigate } from "react-router-dom";
import { useNotification } from "../../contexts/NotificationProvider";

const AdminInfoComponent = ( {
    adminState,
} : {
    adminState: [AdminDetail, React.Dispatch<React.SetStateAction<AdminDetail | null>>],
} ) => {

    const navigate = useNavigate();
    const { notify } = useNotification();

    const [admin, setAdmin] = adminState;
    const [editModalOpen, setEditModalOpen] = useState( false );
    const [isPasswordModalOpen, setIsPasswordModalOpen] = useState( false );
    const { isAdminGeneral } = useAuth();


    const handleDelete = async () => {
        try {
          await administratorsApi.delete(admin.id);
          navigate("/admin/geral/administradores");
        } catch (err) {
          console.error('Failed to delete administrator:', err);
          notify("Failed to delete administrator.", "error");
        }
    }

    return (
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="space-y-6">
          <div>
            <label className="block text-teal-500 font-medium mb-2">
              Username
            </label>
            <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">
              {admin.username}
            </div>
          </div>
          <div>
            <label className="block text-teal-500 font-medium mb-2">Nome</label>
            <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">
              {admin.first_name} {admin.last_name}
            </div>
          </div>
          <div>
            <label className="block text-teal-500 font-medium mb-2">
              Email
            </label>
            <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">
              {admin.email}
            </div>
          </div>
          <div>
            <label className="block text-teal-500 font-medium mb-2">
              Estado{" "}
              <HelpTooltip
                text="Indica se a conta está ativa. Contas inativas não podem aceder à plataforma de administração."
                className="ml-1"
              />
            </label>
            <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">
              {admin.enabled ? (
                <span className="text-green-600 font-medium">Ativo</span>
              ) : (
                <span className="text-red-600 font-medium">Inativo</span>
              )}
            </div>
          </div>
          <div>
            <label className="block text-teal-500 font-medium mb-2">
              Tipo{" "}
              <HelpTooltip
                text="Geral: acesso total à plataforma. Núcleo: apenas gere os núcleos atribuídos. Não é possível alterar o tipo após criação."
                className="ml-1"
              />
            </label>
            <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
              {admin.role === "general_admin"
                ? "Geral"
                : admin.role === "nucleo_admin"
                  ? "Núcleo"
                  : "N/A"}
            </div>
          </div>

          {admin.role === "nucleo_admin" && (
            <div>
              <label className="block text-teal-500 font-medium mb-2">
                Núcleos{" "}
                <HelpTooltip
                  text="Núcleos desportivos que este administrador pode gerir. Pode ser alterado na edição do perfil."
                  className="ml-1"
                />
              </label>
              <div className="bg-gray-100 px-4 py-3 rounded-md">
                {admin.nucleos.length === 0 ? (
                  <span className="text-gray-500">Nenhum núcleo associado</span>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {[...admin.nucleos]
                      .sort((a, b) => a.name.localeCompare(b.name))
                      .map((nucleo) => (
                        <span
                          key={nucleo.id}
                          className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-teal-100 text-teal-800 font-medium"
                        >
                          {nucleo.name}{" "}
                          <span className="ml-1 text-teal-600">
                            ({nucleo.abbreviation})
                          </span>
                        </span>
                      ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {admin.role === "nucleo_admin" && admin.courses.length > 0 && (
            <div>
              <label className="block text-teal-500 font-medium mb-2">
                Cursos Associados
              </label>
              <div className="bg-gray-100 px-4 py-3 rounded-md">
                <div className="flex flex-wrap gap-2">
                  {admin.courses
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
        </div>

        <div className="flex gap-4 mt-8">
          <Button
            onClick={() => setEditModalOpen(true)}
            type="primary"
            active={isAdminGeneral}
            flexible={true}
          >
            Editar
          </Button>
          <Button
            onClick={() => setIsPasswordModalOpen(true)}
            type="info"
            active={isAdminGeneral}
            flexible={true}
          >
            Alterar Password
          </Button>
          <Button
            onClick={handleDelete}
            type="danger"
            active={isAdminGeneral}
            confirmation={{
              title: "Confirmar Eliminação",
              message: `Tem a certeza que deseja eliminar o administrador "${admin.username}"? Esta ação não pode ser desfeita.`,
              confirmLabel: "Eliminar",
              cancelLabel: "Cancelar",
            }}
            flexible={true}
          >
            Eliminar
          </Button>
        </div>

      <AdminEditModal
        controller={[editModalOpen, setEditModalOpen]}
        adminState={[admin, setAdmin]}
        onSaved={(updatedAdmin) => setAdmin(updatedAdmin)}
      />

      <AdminChangePasswordModal
        controller={[isPasswordModalOpen, setIsPasswordModalOpen]}
        adminState={[admin, setAdmin]}
      />
      </div>
    );
}

export default AdminInfoComponent
