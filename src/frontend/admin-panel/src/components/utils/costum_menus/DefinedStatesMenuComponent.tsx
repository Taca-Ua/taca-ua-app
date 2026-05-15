import { useState } from "react";

const DefinedStatesMenuComponent = ( {
    states,
    onSelect,
    initialValue,
    disabled = false
} : {
    states: {value: string, label: string, helpText?: string}[],
    onSelect: (state: string) => void,
    initialValue?: string
    disabled?: boolean
} ) => {

    const [selectedState, setSelectedState] = useState<string | null>(initialValue || null);
    const [hoveredState, setHoveredState] = useState<string | null>(null);

    const handleSelect = (state: string) => {
        setSelectedState(state);
        onSelect(state);
    }

    return (
      <div className="flex gap-2 mb-2">
        {states.map((state) => (
            <div key={state.value} className="flex-1 relative">
              <button
              type="button"
              className={`w-full py-2 rounded-md border transition-colors font-semibold ${selectedState === state.value ? "bg-teal-500 text-white border-teal-600" : "bg-white text-teal-700 border-gray-300"} disabled:opacity-50 disabled:cursor-not-allowed`}
              onClick={() => handleSelect(state.value)}
              onMouseEnter={() => setHoveredState(state.value)}
              onMouseLeave={() => setHoveredState(null)}
              disabled={disabled}
              >
                  {state.label}
              </button>
              {hoveredState === state.value && state.helpText && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-800 text-white text-sm rounded-md shadow-lg z-50 pointer-events-none w-full">
                  <div className="break-words">{state.helpText}</div>
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-gray-800"></div>
                </div>
              )}
            </div>
        ))}
      </div>
    );
}

export default DefinedStatesMenuComponent;
