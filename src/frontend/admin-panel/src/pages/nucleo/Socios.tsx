import NucleoSidebar from '../../components/nucleo_navbar';
import SociosContent from '../socios/SociosContent';

export default function SociosNucleo() {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <NucleoSidebar />
      <SociosContent variant="nucleo" />
    </div>
  );
}
