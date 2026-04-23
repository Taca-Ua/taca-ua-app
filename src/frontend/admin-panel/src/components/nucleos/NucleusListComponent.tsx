import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { nucleosApi, type NucleoListItem } from "../../api/nucleos";

const ListNucleosComponent = ({
    nucleosState,
}: {
    nucleosState?: [NucleoListItem[], React.Dispatch<React.SetStateAction<NucleoListItem[]>>];
}) => {

    const navigate = useNavigate();

    const [nucleos, setNucleos] = nucleosState ? nucleosState : useState<NucleoListItem[]>([]);
    const [searchQuery, setSearchQuery] = useState("");

    useEffect(() => {
        const fetchNucleos = async () => {
            const nucleosList = await nucleosApi.getAll();
            setNucleos(nucleosList);
        };

        fetchNucleos();
    }, []);

    const filteredNucleos = nucleos.filter((n) => n.name.toLowerCase().includes(searchQuery.toLowerCase()) || n.abbreviation.toLowerCase().includes(searchQuery.toLowerCase()));

    return (
        <div className="space-y-3">
            <div className="mb-6">
                <input
                    type="text"
                    placeholder="Pesquisar núcleo..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
            </div>

            {filteredNucleos.sort((a, b) => a.name.localeCompare(b.name)).map((n) => (
                <button
                    key={n.id}
                    type="button"
                    onClick={() => navigate(`/nucleos/${n.id}`)}
                    className="w-full text-left px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors flex justify-between items-center focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center overflow-hidden border-2 border-teal-500 flex-shrink-0">
                        <span className="text-teal-600 font-bold text-sm">{n.abbreviation}</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <span className="text-teal-600 font-bold text-lg">{n.abbreviation}</span>
                        <span className="text-gray-400">|</span>
                        <span className="text-gray-800 font-medium">{n.name}</span>
                    </div>
                </div>
                </button>
            ))}
        </div>
    );
};

export default ListNucleosComponent;
