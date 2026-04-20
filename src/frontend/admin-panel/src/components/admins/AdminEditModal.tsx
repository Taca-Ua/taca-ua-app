import { useEffect, useState } from 'react';
import HelpTooltip from '../HelpTooltip';
import { btn } from '../../styles/buttonStyles';
import { nucleosApi } from '../../api/nucleos';
import { useNotification } from '../../contexts/NotificationProvider';
import { type AdminDetail, administratorsApi } from '../../api/admins';
import DefinedStatesMenuComponent from '../utils/costum_menus/DefinedStatesMenuComponent';
import ChooseMultipleModal from '../utils/costum_menus/ChoseMultipleModel';
import { useAuth } from '../../hooks/useAuth';


interface Nucleo {
  id: string;
  name: string;
  abbreviation: string;
}

const AdminEditModal = ({
  controller,
  adminState,
  onSaved
}: {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>];
  adminState: [AdminDetail, React.Dispatch<React.SetStateAction<AdminDetail | null>>];
  onSaved?: (updatedAdmin: AdminDetail) => void;
} ) => {
  const { notify } = useNotification();
  const [isOpen, setIsOpen] = controller;
  const admin = adminState[0];
  const { isAdminGeneral } = useAuth();

  const [editedFirstName, setEditedFirstName] = useState(admin.first_name);
  const [editedLastName, setEditedLastName] = useState(admin.last_name);
  const [editedEmail, setEditedEmail] = useState(admin.email);
  const [editedEnabled, setEditedEnabled] = useState(admin.enabled);

  const [allNucleos, setAllNucleos] = useState<Nucleo[]>([]);
  const [nucleusSelectModalOpen, setNucleusSelectModalOpen] = useState(false);
  const [selectedNucleos, setSelectedNucleos] = useState<string[]>(admin.nucleos.map(n => n.id));


  useEffect(() => {
    if (!isOpen || !admin) return;
    setEditedFirstName(admin.first_name);
    setEditedLastName(admin.last_name);
    setEditedEmail(admin.email);
    setEditedEnabled(admin.enabled);
    setSelectedNucleos(admin.nucleos.map(n => n.id));
    if (admin.role === 'nucleo_admin') {
      nucleosApi.getAll().then(setAllNucleos).catch(() => setAllNucleos([]));
    } else {
      setAllNucleos([]);  // dont need to load nucleos if not nucleo admin
    }
  }, [isOpen, admin]);

  const handleSave = async () => {
    if (!admin) return;
    if (!editedEmail.trim()) {
      notify('Email é obrigatório', 'error');
      return;
    }
    if (!editedFirstName.trim()) {
      notify('Primeiro nome é obrigatório', 'error');
      return;
    }
    if (!editedLastName.trim()) {
      notify('Último nome é obrigatório', 'error');
      return;
    }
    try {
      await administratorsApi.update(String(admin.id), {
        email: editedEmail,
        first_name: editedFirstName,
        last_name: editedLastName,
        enabled: editedEnabled,
        nucleos: admin.role === 'nucleo_admin' ? selectedNucleos : undefined,
      }).then(updatedAdmin => {
        if (onSaved) onSaved(updatedAdmin);
      }).catch(err => {
        console.error('Failed to update administrator:', err);
        notify('Não foi possível guardar as alterações ao administrador. Verifique os dados e tente novamente.', 'error');
      }).finally(() => {
        onClose();
      });

    } catch (err) {
      notify('Não foi possível guardar as alterações ao administrador. Verifique os dados e tente novamente.', 'error');
    }
  };

  const onClose = () => {
    setEditedFirstName(admin.first_name);
    setEditedLastName(admin.last_name);
    setEditedEmail(admin.email);
    setEditedEnabled(admin.enabled);
    setSelectedNucleos(admin.nucleos.map(n => n.id));
    setIsOpen(false);
  }

  if (!isOpen || !admin) return null;
  if ( !isAdminGeneral ) return null; // should never happen since only general admins can open this modal, but just in case

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Administrador {admin.role === 'general_admin' ? 'Geral' : admin.role === 'nucleo_admin' ? 'Núcleo' : 'N/A'}</h2>
        <div className="overflow-y-auto flex-1 pr-2 pl-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 font-medium mb-2">Username</label>
              <div className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-600">
                {admin.username}
              </div>
              <p className="text-xs text-gray-500 mt-1">O username não pode ser alterado</p>
            </div>
            <div>
              <label className="block text-gray-700 font-medium mb-2">Email <span className="text-red-500">*</span></label>
              <input
                type="email"
                value={editedEmail}
                onChange={e => setEditedEmail(e.target.value)}
                placeholder="Digite o email"
                required
                className="w-full text-gray-700 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div>
              <label className="block text-gray-700 font-medium mb-2">Primeiro Nome <span className="text-red-500">*</span></label>
              <input
                type="text"
                value={editedFirstName}
                onChange={e => setEditedFirstName(e.target.value)}
                placeholder="Digite o primeiro nome"
                required
                className="w-full text-gray-700 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div>
              <label className="block text-gray-700 font-medium mb-2">Último Nome <span className="text-red-500">*</span></label>
              <input
                type="text"
                value={editedLastName}
                onChange={e => setEditedLastName(e.target.value)}
                placeholder="Digite o último nome"
                required
                className="w-full text-gray-700 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div className='md:col-span-2'>
              <label className="block text-gray-700 font-medium mb-2">Estado <HelpTooltip text="Ativo: o administrador pode aceder ao sistema. Inativo: acesso bloqueado sem eliminar a conta." className="ml-1" /></label>
              <DefinedStatesMenuComponent
                states={[
                  {value: 'true', label: 'Ativo'},
                  {value: 'false', label: 'Inativo'},
                ]}
                onSelect={(value) => setEditedEnabled(value === 'true')}
                initialValue={editedEnabled ? 'true' : 'false'}
              />
            </div>
          </div>
          {admin.role === 'nucleo_admin' && (
            <div className="mt-6 md:col-span-2 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <label className="block text-gray-700 font-medium mb-4">
                Núcleos{" "}
                <HelpTooltip
                  text="Selecione os núcleos desportivos que este administrador poderá gerir. Apenas aplicável para o tipo Administrador Núcleo."
                  className="ml-1"
                />
              </label>
              <button
                type="button"
                onClick={() => setNucleusSelectModalOpen(true)}
                className={`w-full mb-4 px-4 py-2.5 ${btn.secondary} rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 hover:shadow-md`}
              >
                Selecionar Núcleos
              </button>
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
          <button
            onClick={onClose}
            className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md`}
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            className={`flex-1 px-4 py-2 ${btn.primary} rounded-md`}
          >
            Guardar
          </button>
        </div>
      </div>

      {/* Núcleos Modal */}
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

export default AdminEditModal;
