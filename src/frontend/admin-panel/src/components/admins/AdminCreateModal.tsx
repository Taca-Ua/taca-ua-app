import { useEffect, useState } from "react";
import HelpTooltip from "../HelpTooltip";
import { useNotification } from "../../contexts/NotificationProvider";
import { administratorsApi } from "../../api/admins";
import { nucleosApi } from "../../api/nucleos";
import ChooseMultipleModal from "../utils/costum_menus/ChoseMultipleModal";
import DefinedStatesMenuComponent from "../utils/costum_menus/DefinedStatesMenuComponent";
import { useAuth } from "../../hooks/useAuth";
import Button from "../utils/Button";

const AdminCreateModal = ({
  controller,
  onCreated
} : {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>];
  onCreated?: (admin: any) => void;
}) => {
  const [isOpen, setIsOpen] = controller;
	const { notify } = useNotification();
  const { isAdminGeneral } = useAuth();

	const [memberUserName, setMemberUserName] = useState('');
	const [memberFirstName, setMemberFirstName] = useState('');
	const [memberLastName, setMemberLastName] = useState('');
	const [memberPassword, setMemberPassword] = useState('');
	const [memberRole, setMemberRole] = useState<'general_admin' | 'nucleo_admin'>('general_admin');
	const [email, setEmail] = useState('');
	const [confirmPassword, setConfirmPassword] = useState('');
	const [showPassword, setShowPassword] = useState(false);
	const [showConfirmPassword, setShowConfirmPassword] = useState(false);
	const [allNucleos, setAllNucleos] = useState<any[]>([]);
	const [selectedNucleos, setSelectedNucleos] = useState<string[]>([]);

	const [nucleusSelectModalOpen, setNucleusSelectModalOpen] = useState(false);

	useEffect(() => {
		if (!isOpen) return;
		nucleosApi.getAll().then(setAllNucleos).catch(() => setAllNucleos([]));
	}, [isOpen]);

	const handleAddMember = async () => {
		if (!memberUserName.trim()) {
			notify('Username é obrigatório', 'error');
			return;
		}
		if (!memberFirstName.trim()) {
			notify('Primeiro nome é obrigatório', 'error');
			return;
		}
		if (!memberLastName.trim()) {
			notify('Último nome é obrigatório', 'error');
			return;
		}
		if (!email.trim()) {
			notify('Email é obrigatório', 'error');
			return;
		}
		if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 254) {
			notify('Email inválido', 'error');
			return;
		}
		if (!memberPassword.trim()) {
			notify('Password é obrigatória', 'error');
			return;
		}
		if (memberPassword.length < 8) {
			notify('Password deve ter pelo menos 8 caracteres', 'error');
			return;
		}
		if (!confirmPassword.trim()) {
			notify('Confirmação de password é obrigatória', 'error');
			return;
		}
		if (memberPassword !== confirmPassword) {
			notify('As passwords não coincidem', 'error');
			return;
		}

		try {
			const newAdmin = await administratorsApi.create({
				username: memberUserName,
				password: memberPassword,
				first_name: memberFirstName,
				last_name: memberLastName,
				email,
				role: memberRole,
				nucleos: memberRole === 'nucleo_admin' ? selectedNucleos : [],
			});
			if (onCreated) onCreated(newAdmin);
			onClose();
      notify('Administrador criado com sucesso!', 'success');
		} catch (err) {
			notify('Não foi possível criar o administrador. Erro interno.', 'error');
		}
	};

	const onClose = () => {
    setIsOpen(false);
		setMemberUserName('');
		setMemberFirstName('');
		setMemberLastName('');
		setMemberPassword('');
		setConfirmPassword('');
		setShowPassword(false);
		setShowConfirmPassword(false);
		setMemberRole('general_admin');
		setEmail('');
		setSelectedNucleos([]);
	};

	if (!isOpen) return null;
	if (!isAdminGeneral) return null; // Only general admins can create new admins

	return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
      <div className="bg-white rounded-lg p-8 max-w-4xl w-full mx-4 animate-slideUp max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">
          Adicionar Administrador
        </h2>
        <div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="memberUserName"
                className="block text-gray-700 font-medium mb-2"
              >
                Username{" "}
                <HelpTooltip
                  text="Nome único de identificação do administrador, usado para aceder à plataforma. Não pode ser alterado após criação."
                  className="ml-1"
                />{" "}
                <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="memberUserName"
                value={memberUserName}
                onChange={(e) => setMemberUserName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Digite o username"
              />
            </div>
            <div>
              <label
                htmlFor="email"
                className="block text-gray-700 font-medium mb-2"
              >
                Email{" "}
                <HelpTooltip
                  text="Endereço de email institucional do administrador. Utilizado para notificações e recuperação de conta."
                  className="ml-1"
                />{" "}
                <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Digite o email (ex: admin@ua.pt)"
              />
            </div>
            <div>
              <label
                htmlFor="memberFirstName"
                className="block text-gray-700 font-medium mb-2"
              >
                Primeiro Nome <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="memberFirstName"
                value={memberFirstName}
                onChange={(e) => setMemberFirstName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Digite o primeiro nome"
              />
            </div>
            <div>
              <label
                htmlFor="memberLastName"
                className="block text-gray-700 font-medium mb-2"
              >
                Último Nome <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="memberLastName"
                value={memberLastName}
                onChange={(e) => setMemberLastName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Digite o último nome"
              />
            </div>
            <div>
              <label
                htmlFor="memberPassword"
                className="block text-gray-700 font-medium mb-2"
              >
                Password{" "}
                <HelpTooltip
                  text="A password deve ter no mínimo 8 caracteres. Utilize uma combinação de letras, números e símbolos para maior segurança."
                  className="ml-1"
                />{" "}
                <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  id="memberPassword"
                  value={memberPassword}
                  onChange={(e) => setMemberPassword(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 pr-10"
                  placeholder="Digite a password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268-2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                      />
                    </svg>
                  ) : (
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                      />
                    </svg>
                  )}
                </button>
              </div>
            </div>
            <div>
              <label
                htmlFor="memberConfirmPassword"
                className="block text-gray-700 font-medium mb-2"
              >
                Confirmar Password{" "}
                <HelpTooltip
                  text="Repita exatamente a password inserida ao lado para garantir que não houve erros de digitação."
                  className="ml-1"
                />{" "}
                <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  id="memberConfirmPassword"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 pr-10"
                  placeholder="Confirme a password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  tabIndex={-1}
                >
                  {showConfirmPassword ? (
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268-2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                      />
                    </svg>
                  ) : (
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                      />
                    </svg>
                  )}
                </button>
              </div>
            </div>
            <div className="md:col-span-2">
              <label
                htmlFor="memberRole"
                className="block text-gray-700 font-medium mb-2"
              >
                Tipo{" "}
                <HelpTooltip
                  text="Administrador Geral tem acesso total à plataforma. Administrador Núcleo só pode gerir os núcleos que lhe forem atribuídos."
                  className="ml-1"
                />{" "}
                <span className="text-red-500">*</span>
              </label>
              <DefinedStatesMenuComponent
                states={[
                  { value: 'general_admin', label: 'Administrador Geral' },
                  { value: 'nucleo_admin', label: 'Administrador Núcleo' },
                ]}
                onSelect={(state) => setMemberRole(state as 'general_admin' | 'nucleo_admin')}
              />
            </div>
          </div>
          {memberRole === "nucleo_admin" && (
            <div className="mt-6 md:col-span-2 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <label className="block text-gray-700 font-medium mb-4">
                Núcleos{" "}
                <HelpTooltip
                  text="Selecione os núcleos desportivos que este administrador poderá gerir. Apenas aplicável para o tipo Administrador Núcleo."
                  className="ml-1"
                />
              </label>
              <Button
                onClick={() => setNucleusSelectModalOpen(true)}
                type="secondary"
              >
                Selecionar Núcleos
              </Button>
              {selectedNucleos.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-300">
                  <p className="text-gray-600 text-sm font-semibold mb-3">
                    Selecionados ({selectedNucleos.length}):
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {allNucleos
                      .filter((n) => selectedNucleos.includes(n.id))
                      .sort((a, b) => a.name.localeCompare(b.name))
                      .map((n) => (
                        <span
                          key={n.id}
                          className="inline-flex items-center gap-2 bg-teal-500 text-white text-sm font-medium px-3 py-1.5 rounded-full hover:bg-teal-600 transition-colors"
                        >
                          <span className="font-semibold">
                            {n.abbreviation}
                          </span>
                          <button
                            type="button"
                            onClick={() =>
                              setSelectedNucleos(
                                selectedNucleos.filter((id) => id !== n.id),
                              )
                            }
                            className="text-white hover:text-gray-100 font-bold leading-none"
                            tabIndex={-1}
                            title="Remover"
                          >
                            ✕
                          </button>
                        </span>
                      ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        <div className="flex gap-4 mt-6 flex-shrink-0">
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

      <ChooseMultipleModal
        controller={[nucleusSelectModalOpen, setNucleusSelectModalOpen]}
        allElementsLoader={() => {
          let a = nucleosApi
            .getAll()
            .then((nucleos) =>
              nucleos.map((n: any) => ({
                id: n.id,
                title: n.name,
                subTitle: n.abbreviation,
              })),
            )
            .catch(() => []);
          return a;
        }}
        initialChosenElementsIds={selectedNucleos}
        onSave={(chosenIds) =>
          setSelectedNucleos(chosenIds.map((elem) => elem.id))
        }
        title="Selecionar Núcleos"
      />
    </div>
  );
};

export default AdminCreateModal;
