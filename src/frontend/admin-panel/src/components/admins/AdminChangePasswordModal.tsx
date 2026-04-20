import { useState } from "react";
import { type AdminDetail, administratorsApi } from "../../api/admins"
import HelpTooltip from "../HelpTooltip";
import { useAuth } from "../../hooks/useAuth";
import Button from "../utils/Button";

const AdminChangePasswordModal = ( {
    controller,
    adminState,
    onChangePasswordSuccess,
} : {
    controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>]
    adminState: [AdminDetail, React.Dispatch<React.SetStateAction<AdminDetail | null>>],
    onChangePasswordSuccess?: () => void,
} ) => {
    const [isOpen, setIsOpen] = controller;
    const admin = adminState[0];
    const { isAdminGeneral } = useAuth();

    const [newPassword, setNewPassword] = useState('');
    const [confirmNewPassword, setConfirmNewPassword] = useState('');
    const [showNewPassword, setShowNewPassword] = useState(false);
    const [showConfirmNewPassword, setShowConfirmNewPassword] = useState(false);

    const onClose = () => {
        setIsOpen(false);
        setNewPassword('');
        setConfirmNewPassword('');
        setShowNewPassword(false);
        setShowConfirmNewPassword(false);
    };

    const handleChangePassword = async () => {
        if (!newPassword.trim()) {
            alert('Password é obrigatória');
            return;
        }
        if (!confirmNewPassword.trim()) {
            alert('Confirmação de password é obrigatória');
            return;
        }
        if (newPassword !== confirmNewPassword) {
            alert('As passwords não coincidem');
            return;
        }

        const changePasswordResult = async () => {
            try {
                await administratorsApi.changePassword(admin.id, {
                    new_password: newPassword,
                    temporary: false
                });
                alert('Password alterada com sucesso!');
                if (onChangePasswordSuccess) onChangePasswordSuccess();
                onClose();
            } catch (error) {
                console.error('Error changing password:', error);
                alert('Ocorreu um erro ao alterar a password. Por favor, tente novamente.');
            }
        };
        await changePasswordResult();
    };

    if ( !isOpen ) return null;
    if ( !isAdminGeneral ) return null; // Only general admins can change passwords

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Alterar Password</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                    Nova Password
                    <HelpTooltip
                        text="A password deve ter no mínimo 8 caracteres. Após guardar, o administrador deverá usar a nova password no próximo login."
                        className="ml-1"
                    />
                    <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <input
                    type={showNewPassword ? 'text' : 'password'}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Digite a nova password"
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 pr-10"
                  />
                  <button type="button" onClick={() => setShowNewPassword(!showNewPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" tabIndex={-1}>
                    {showNewPassword
                      ? <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                      : <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                    }
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-gray-700 font-medium mb-2">Confirmar Password <HelpTooltip text="Repita exatamente a nova password para confirmar que não houve erros de digitação." className="ml-1" /> <span className="text-red-500">*</span></label>
                <div className="relative">
                  <input
                    type={showConfirmNewPassword ? 'text' : 'password'}
                    value={confirmNewPassword}
                    onChange={(e) => setConfirmNewPassword(e.target.value)}
                    placeholder="Confirme a nova password"
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 pr-10"
                  />
                  <button type="button" onClick={() => setShowConfirmNewPassword(!showConfirmNewPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" tabIndex={-1}>
                    {showConfirmNewPassword
                      ? <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                      : <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                    }
                  </button>
                </div>
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
                onClick={handleChangePassword}
                type="primary"
                flexible={true}
              >
                Alterar Password
              </Button>
            </div>
          </div>
        </div>
    );
}

export default AdminChangePasswordModal;
