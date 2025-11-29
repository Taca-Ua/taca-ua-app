interface GameCardProps {
  title: string;
  team1: string;
  team2: string;
  modalidade: string;
  time?: string;
  onClick?: () => void;
}

function GameCard({ title, team1, team2, modalidade, time, onClick }: GameCardProps) {
  return (
    <div 
      onClick={onClick}
      className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-sm text-gray-500 mb-1">Jogo</p>
          <h3 className="text-xl font-bold text-gray-800">{title}</h3>
        </div>
        <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
          <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
      </div>
      <div className="mb-4">
        <p className="text-gray-700">
          <span className="font-semibold">{team1}</span> vs <span className="font-semibold">{team2}</span>
        </p>
        <p className="text-sm text-teal-600 mt-1">{modalidade}</p>
      </div>
      {time && (
        <p className="text-sm text-gray-500">
          Hora: {time}
        </p>
      )}
    </div>
  );
}

export default GameCard;
