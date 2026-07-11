import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { nucleosApi, type NucleoListItem } from "../../api/nucleos";
import LazyImage from "../utils/LazyImage";

const NucleusEntry = ({ nucleus }: { nucleus: NucleoListItem }) => {

    const elementIsDisabled = (nucleus.belongs_to_season === undefined)? false : !nucleus.belongs_to_season;

    return (
      <Link
        to={`/nucleos/${nucleus.id}`}
        className={"cursor-pointer bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border border-gray-200 p-6 flex flex-col gap-4" + (elementIsDisabled ? " opacity-50" : "")}
      >
        <div className="flex items-center justify-center text-center gap-10">
          {nucleus.logo_url ? (
            <LazyImage
              src={nucleus.logo_url}
              alt={nucleus.name}
              className="h-24 object-cover"
            />
          ) : (
            <div className="w-24 h-24 rounded-full bg-teal-50 flex items-center justify-center border-2 border-teal-500">
              <span className="text-teal-600 font-bold text-sm">
                {nucleus.abbreviation}
              </span>
            </div>
          )}
          <div>
            <span className="text-teal-600 font-bold text-lg block">
              {nucleus.abbreviation}
            </span>
            <span className="text-gray-800 font-medium text-sm block">
              {nucleus.name}
            </span>
          </div>
        </div>
      </Link>
    );
}

const ListNucleosComponent = ({
    nucleosState,
}: {
    nucleosState?: [NucleoListItem[], React.Dispatch<React.SetStateAction<NucleoListItem[]>>];
}) => {

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

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredNucleos.sort((a, b) => a.name.localeCompare(b.name)).map((n) => (
                    <NucleusEntry key={n.id} nucleus={n} />
                ))}
            </div>
        </div>
    );
};

export default ListNucleosComponent;
