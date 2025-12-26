import { Link } from 'react-router-dom';

interface TournamentCardProps {
  id: string;
  name: string;
  modality: string;
  epoca: string;
  icon: string;
}

function TournamentCard({ id, name, modality, epoca, icon }: TournamentCardProps) {
  return (
    <Link
      to={`/classificacao/torneio/${id}`}
      className="bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden group flex flex-col h-full"
    >
      <div className="p-6 flex-grow">
        <div className="flex items-center justify-center w-16 h-16 bg-teal-100 rounded-full mb-4 group-hover:bg-teal-200 transition-colors">
          <span className="text-3xl">{icon}</span>
        </div>
        <h3 className="text-xl font-bold text-gray-800 mb-2 group-hover:text-teal-600 transition-colors">
          {name}
        </h3>
        <p className="text-gray-600 mb-1">{modality}</p>
        <p className="text-sm text-gray-500">Época {epoca}</p>
      </div>
      <div className="bg-gray-50 px-6 py-3 group-hover:bg-teal-50 transition-colors mt-auto">
        <span className="text-teal-600 font-medium group-hover:text-teal-700">
          Ver Classificação →
        </span>
      </div>
    </Link>
  );
}

export default TournamentCard;
