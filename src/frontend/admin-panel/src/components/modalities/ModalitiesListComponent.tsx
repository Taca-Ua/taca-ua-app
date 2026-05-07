import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { type ModalityListItem } from "../../api/modalities";


const ModalitiesListComponent = ({
  modalities,
} : {
  modalities: ModalityListItem[];
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  const filteredModalities = modalities.filter(mod => {
    const matchesSearch = mod.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = typeFilter ? mod.modality_type?.id === typeFilter : true;
    return matchesSearch && matchesType;
  });

  const sortedModalities = filteredModalities
    .sort((a, b) => a.name.localeCompare(b.name))
    .sort(a => a.belongs_to_season ? -1 : 1); // Modalidades que pertencem à temporada aparecem primeiro

  if (modalities.length === 0) {
    return (
      <p className="text-gray-500 text-center py-8">
        Nenhuma modalidade encontrada.
      </p>
    );
  }

  const ModalityEntry = (mod: ModalityListItem) => {
    const navigate = useNavigate();
    return (
      <button
        type="button"
        onClick={() => navigate(`/modalidades/${mod.id}`)}
        className="w-full text-left px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors flex justify-between items-center focus:outline-none focus:ring-2 focus:ring-teal-500"
      >
        <span className="text-gray-800 font-medium">{mod.name}</span>
        {mod.modality_type && (
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
            {mod.modality_type.name}
          </span>
        )}
      </button>
    );
  };

  return (
    <div className="space-y-3">
      <div className="mb-6 flex gap-3">
        <input
          type="text"
          placeholder="Pesquisar modalidade..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
        />
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
        >
          <option value="">Todos os tipos</option>
          {[
            ...new Map(
              modalities
                .filter((m): m is ModalityListItem & { modality_type: NonNullable<ModalityListItem["modality_type"]> } => m.modality_type !== null && m.modality_type !== undefined)
                .map(m => [m.modality_type.id, m.modality_type])
            ).values()
          ]
            .filter((a): a is { id: string; name: string } => a !== undefined)
            .sort((a, b) => a.name.localeCompare(b.name))
            .map(t => (
              t ? <option key={t.id} value={t.id}>{t.name}</option> : null
            ))}
        </select>
      </div>

      {sortedModalities.map((mod) => (
        <ModalityEntry key={mod.id} {...mod} />
      ))}
    </div>
  );
};

export default ModalitiesListComponent;
