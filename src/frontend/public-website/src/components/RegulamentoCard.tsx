interface RegulamentoCardProps {
  title: string;
  category: string;
  epoca: string;
  onClick: () => void;
}

function RegulamentoCard({ title, category, epoca, onClick }: RegulamentoCardProps) {
  return (
    <button
      onClick={onClick}
      className="bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden group text-left w-full"
    >
      <div className="p-6">
        <div className="flex items-center justify-center w-16 h-16 bg-indigo-100 rounded-full mb-4 group-hover:bg-indigo-200 transition-colors">
          <svg
            className="w-8 h-8 text-indigo-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <p className="text-sm text-gray-500 mb-1">{category}</p>
        <h3 className="text-2xl font-bold text-gray-900 mb-2 group-hover:text-teal-600 transition-colors">
          {title}
        </h3>
        <p className="text-sm text-teal-600 font-medium">{epoca}</p>
      </div>
    </button>
  );
}

export default RegulamentoCard;
