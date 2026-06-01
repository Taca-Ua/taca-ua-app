import { useState } from "react";

type TabSystemElement = {
    id: string;
    label: string;
    content: React.ReactNode;
}

const TabSystem = ( {
    elements,
    onTabChange
} : {
    elements: TabSystemElement[];
    onTabChange?: (tabId: string) => void;
    saveState?: boolean;
} ) => {

    const [activeTab, setActiveTab] = useState<string>(elements[0]?.id ?? "");
    const activeContent = elements.find(e => e.id === activeTab)?.content;

    return (
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="border-b border-gray-200">
          <div className="flex">
            {elements.map((element) => (
              <button
                onClick={() => {
                  setActiveTab(element.id);
                  if (onTabChange) onTabChange(element.id);
                }}
                className={`px-6 py-4 font-bold text-2xl transition-colors border-b-2 ${
                  activeTab === element.id
                    ? "border-teal-500 text-teal-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                {element.label}
              </button>
            ))}
          </div>
        </div>
        <div className="w-full p-4 border-b">{activeContent}</div>
      </div>
    );
}

export default TabSystem;
