import { useEffect, useState, useRef } from "react";
import Button from "../Button";
import { useModal } from "../../../contexts/ModalContext";

const ChoseOneModal = ( {
    allElementsLoader,
    onSelect,
    title = "Escolha uma opção",
    initialSelectedId,
    hideClearButton = false
} : {
    allElementsLoader: () => Promise<{id: string, title: string, subTitle?: string}[]>,
    onSelect: (element: {id: string, title: string, subTitle?: string} | null) => void,
    title?: string
    initialSelectedId?: string
    hideClearButton?: boolean
} ) => {
    const { popModal } = useModal();
    const searchInputRef = useRef<HTMLInputElement>(null);

    const [allElements, setAllElements] = useState<{id: string, title: string, subTitle?: string}[]>([]);
    const [searchQuery, setSearchQuery] = useState("");
    const [chosenElement, setChosenElement] = useState<string>("");

    const filteredElements = allElements.filter((element) =>
        element.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (element.subTitle && element.subTitle.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    useEffect(() => {
        allElementsLoader().then(elements => {
            setAllElements(elements);
            setChosenElement(initialSelectedId || "");
        }).catch(err => {
            console.error("Failed to load elements:", err);
            setAllElements([]);
        });
    }, [allElementsLoader]);

    // Focus the search input on mount
    useEffect(() => {
      if (searchInputRef.current) {
        searchInputRef.current.focus();
      }
    }, []);

    const onClose = () => {
        popModal();
    }

    const handleSelect = (element: {id: string, title: string, subTitle?: string}) => {
        setChosenElement(element.id);
        onSelect(element);
        onClose();
    };

    const renderElement = (element: {id: string, title: string, subTitle?: string}) => {
        return (
          <div
            key={element.id}
            onClick={() => handleSelect(element)}
            className={`flex items-center justify-between px-4 py-3 rounded-md cursor-pointer transition-colors bg-gray-50 hover:bg-gray-200 ${chosenElement === element.id ? "bg-teal-50 border-teal-300 border" : ""}`}
          >
            <div className="flex items-center gap-3">
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0 ${chosenElement === element.id ? "bg-teal-500 text-white" : "bg-gray-200 text-gray-600"}`}
              >
                {element.title.charAt(0).toUpperCase()}
              </div>
              <div>
                <p className="font-medium text-gray-800">{element.title}</p>
                <p className="text-sm text-gray-500">{element.subTitle}</p>
              </div>
            </div>
          </div>
        );
    }

    return (
        <div className="bg-white rounded-lg p-8 max-w-max w-full min-w-[500px] mx-4 max-h-[80vh] flex flex-col">
          <h2 className="text-2xl font-bold mb-4 text-gray-800">
            {title}
          </h2>

          {/* Search, Filter, and Results */}
          <div
            className="grid grid-cols-1 gap-6 flex-1 min-h-0"
          >
            <div className="min-h-0 flex flex-col">
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-4">
                <input
                  ref={searchInputRef}
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Pesquisar ..."
                  className="w-full sm:w-auto flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>

              <div className="flex-1 overflow-y-auto space-y-2 mb-3 max-h-96 lg:max-h-none relative">
                {filteredElements.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">
                    {allElements.length === 0
                      ? "Nenhum elemento disponível"
                      : "Nenhum resultado para a pesquisa"}
                  </p>
                ) : (
                  <>
                    {/* Sticky selected element at the top */}
                    {chosenElement && (
                      <div className="sticky top-0 z-10 bg-white">
                        {renderElement(allElements.find(ele => ele.id === chosenElement)!)}
                      </div>
                    )}

                    {/* Other elements except the selected one */}
                    {filteredElements
                      .filter(element => element.id !== chosenElement)
                      .map((element: {id: string, title: string, subTitle?: string}) => renderElement(element))}
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex gap-4 flex-shrink-0">
            <Button
              onClick={onClose}
              type="secondary"
              flexible={true}
            >
              Cancelar
            </Button>
            <Button
              onClick={() => {
                setChosenElement("")
                onSelect(null)
                onClose()
              }}
              type="primary"
              flexible={true}
              active={!hideClearButton}
            >
              Limpar
            </Button>
          </div>
        </div>
    );
};

export default ChoseOneModal;
