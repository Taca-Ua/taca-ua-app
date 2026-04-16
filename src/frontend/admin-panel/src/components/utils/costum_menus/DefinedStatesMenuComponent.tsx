import { useState } from "react";

const DefinedStatesMenuComponent = ( {
    states,
    onSelect,
} : {
    states: {value: string, label: string}[],
    onSelect: (state: string) => void,
} ) => {

    const [selectedState, setSelectedState] = useState<string | null>(null);

    const handleSelect = (state: string) => {
        setSelectedState(state);
        onSelect(state);
    }

    return (
      <div className="flex gap-2 mb-2">
        {states.map((state) => (
            <button
            type="button"
            className={`flex-1 py-2 rounded-md border transition-colors font-semibold ${selectedState === state.value ? "bg-teal-500 text-white border-teal-600" : "bg-white text-teal-700 border-gray-300"}`}
            onClick={() => handleSelect(state.value)}
            >
                {state.label}
            </button>
        ))}
      </div>
    );
}

export default DefinedStatesMenuComponent;
