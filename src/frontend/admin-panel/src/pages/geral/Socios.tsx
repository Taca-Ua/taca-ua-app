import Sidebar from '../../components/geral_navbar';
import SociosContent from '../socios/SociosContent';

export default function SociosGeral() {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <SociosContent variant="geral" />
    </div>
  );
}
