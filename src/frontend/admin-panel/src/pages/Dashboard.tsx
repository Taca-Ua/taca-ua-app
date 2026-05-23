import { useAuth } from "../hooks/useAuth"
import DashboardGeral from "./geral/DashboardGeral";
import DashboardNucleo from "./nucleo/DashboardNucleo";

const Dashboard = () => {
    const { username, adminRole } = useAuth();

    if (adminRole === 'general_admin') {
        return (
            <DashboardGeral />
        );
    }

    if (adminRole === 'nucleo_admin') {
        return (
            <DashboardNucleo />
        );
    }

    return (
        <div className="p-6 bg-white rounded shadow">
            <h1 className="text-2xl font-bold mb-4">Bem-vindo, {username}!</h1>
            <p className="text-gray-700">Este é o seu painel de controle. Use a barra lateral para navegar pelas seções administrativas.</p>
        </div>
    );
}

export default Dashboard;
