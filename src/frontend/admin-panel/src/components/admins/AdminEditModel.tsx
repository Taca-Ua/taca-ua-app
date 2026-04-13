import { useEffect, useState } from 'react';
import HelpTooltip from '../HelpTooltip';
import { btn } from '../../styles/buttonStyles';
import { nucleosApi } from '../../api/nucleos';
import { useNotification } from '../../contexts/NotificationProvider';
import { type AdminDetail, administratorsApi } from '../../api/admins';


interface Nucleo {
  id: string;
  name: string;
  abbreviation: string;
}

interface AdminEditModelProps {
  isOpen: boolean;
  admin: AdminDetail | null;
  onClose: () => void;
  onSaved?: (updatedAdmin: AdminDetail) => void;
}

const AdminEditModel = ({ isOpen, admin, onClose, onSaved }: AdminEditModelProps) => {
  const { notify } = useNotification();
  const [editedFirstName, setEditedFirstName] = useState('');
  const [editedLastName, setEditedLastName] = useState('');
  const [editedEmail, setEditedEmail] = useState('');
  const [editedEnabled, setEditedEnabled] = useState(true);
  const [allNucleos, setAllNucleos] = useState<Nucleo[]>([]);
  const [editedNucleos, setEditedNucleos] = useState<string[]>([]);
  const [nucleoSearchEdit, setNucleoSearchEdit] = useState('');

  useEffect(() => {
    if (!isOpen || !admin) return;
    setEditedFirstName(admin.first_name);
    setEditedLastName(admin.last_name);
    setEditedEmail(admin.email);
    setEditedEnabled(admin.enabled);
    setEditedNucleos(admin.nucleos.map(n => n.id));
    nucleosApi.getAll().then(setAllNucleos).catch(() => setAllNucleos([]));
    setNucleoSearchEdit('');
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
        nucleos: admin.role === 'nucleo_admin' ? editedNucleos : undefined,
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

  if (!isOpen || !admin) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Administrador</h2>
        <div className="overflow-y-auto flex-1 pr-2">
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
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
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
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
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
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div>
              <label className="block text-gray-700 font-medium mb-2">Estado <HelpTooltip text="Ativo: o administrador pode aceder ao sistema. Inativo: acesso bloqueado sem eliminar a conta." className="ml-1" /></label>
              <select
                value={editedEnabled ? 'true' : 'false'}
                onChange={e => setEditedEnabled(e.target.value === 'true')}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
              >
                <option value="true">Ativo</option>
                <option value="false">Inativo</option>
              </select>
            </div>
            <div>
              <label className="block text-gray-700 font-medium mb-2">Tipo</label>
              <div className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-600">
                {admin.role === 'general_admin' ? 'Geral' : admin.role === 'nucleo_admin' ? 'Núcleo' : 'N/A'}
              </div>
              <p className="text-xs text-gray-500 mt-1">O tipo não pode ser alterado</p>
            </div>
          </div>
          {admin.role === 'nucleo_admin' && (
            <div className="mt-4">
              <label className="block text-gray-700 font-medium mb-2">Núcleos</label>
              <input
                type="text"
                value={nucleoSearchEdit}
                onChange={e => setNucleoSearchEdit(e.target.value)}
                placeholder="Pesquisar núcleo..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 mb-2"
              />
              <div className="border border-gray-300 rounded-md max-h-40 overflow-y-auto p-2 space-y-1">
                {allNucleos.length === 0 ? (
                  <p className="text-gray-500 text-sm p-2">A carregar núcleos...</p>
                ) : (
                  [...allNucleos]
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .filter(n => n.name.toLowerCase().includes(nucleoSearchEdit.toLowerCase()) || n.abbreviation.toLowerCase().includes(nucleoSearchEdit.toLowerCase()))
                    .map(nucleo => (
                      <label key={nucleo.id} className="flex items-center gap-2 px-2 py-1 rounded hover:bg-gray-50 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={editedNucleos.includes(nucleo.id)}
                          onChange={e => {
                            if (e.target.checked) {
                              setEditedNucleos([...editedNucleos, nucleo.id]);
                            } else {
                              setEditedNucleos(editedNucleos.filter(nid => nid !== nucleo.id));
                            }
                          }}
                          className="accent-teal-500"
                        />
                        <span className="text-gray-800">{nucleo.name}</span>
                        <span className="text-gray-500 text-sm">({nucleo.abbreviation})</span>
                      </label>
                    ))
                )}
              </div>
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
    </div>
  );
};

export default AdminEditModel;
