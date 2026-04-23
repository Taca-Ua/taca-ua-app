import { useEffect, useMemo, useState } from "react";
import Button from "../Button";
import { useModal } from "../../../contexts/ModalContext";

export interface GenericElement {
    id: string;
    title: string;
    subTitle: string;
}

const EditSummary = ({
    newlySelected,
    newlyDeselected,
    className = "",
}: {
    newlySelected: GenericElement[];
    newlyDeselected: GenericElement[];
    className?: string;
}) => (
    <div className={`space-y-4 overflow-y-auto pr-1 ${className}`}>
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-green-700 mb-2">
          Novos selecionados ({newlySelected.length})
        </p>
        {newlySelected.length === 0 ? (
          <p className="text-sm text-gray-500">Sem novos selecionados.</p>
        ) : (
          <ul className="space-y-2">
            {newlySelected.map((element) => (
              <li
                key={`added-${element.id}`}
                className="text-sm text-green-800 bg-green-50 border border-green-200 rounded px-2 py-1"
              >
                <span className="font-medium">{element.title}</span>
                {element.subTitle ? ` - ${element.subTitle}` : ""}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-red-700 mb-2">
          Serão removidos ({newlyDeselected.length})
        </p>
        {newlyDeselected.length === 0 ? (
          <p className="text-sm text-gray-500">Sem remoções.</p>
        ) : (
          <ul className="space-y-2">
            {newlyDeselected.map((element) => (
              <li
                key={`removed-${element.id}`}
                className="text-sm text-red-800 bg-red-50 border border-red-200 rounded px-2 py-1"
              >
                <span className="font-medium">{element.title}</span>
                {element.subTitle ? ` - ${element.subTitle}` : ""}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
);

const ChooseMultipleModal = ({
    allElementsLoader,
    initialChosenElementsIds = [],
    onSave,
    title = "Escolha os elementos",
    showSummary = false,
}: {
    allElementsLoader: () => Promise<GenericElement[]>;
    initialChosenElementsIds?: string[];
    onSave: (chosen: GenericElement[]) => void;
    title?: string;
    showSummary?: boolean;
}) => {
    const { popModal } = useModal();

    const [allElements, setAllElements] = useState<GenericElement[]>([]);
    const [chosenElements, setChosenElements] = useState<string[]>(initialChosenElementsIds);

    const [searchQuery, setSearchQuery] = useState("");
    const [isMobileSummaryOpen, setIsMobileSummaryOpen] = useState(false);


    useEffect(() => {
        allElementsLoader().then(setAllElements);
        setChosenElements(initialChosenElementsIds);
    }, []);


    // Filter type: 'all', 'selected', 'not_selected'
    const [filterType, setFilterType] = useState<'all' | 'selected' | 'not_selected'>('all');

    const filteredElements = allElements.filter((element) => {
      const matchesSearch = element.title.toLowerCase().includes(searchQuery.toLowerCase());
      if (!matchesSearch) return false;
      if (filterType === 'all') return true;
      if (filterType === 'selected') return chosenElements.includes(element.id);
      if (filterType === 'not_selected') return !chosenElements.includes(element.id);
      return true;
    });

    const { newlySelected, newlyDeselected } = useMemo(() => {
      const initialIds = new Set(initialChosenElementsIds);
      const currentIds = new Set(chosenElements);

      const added = allElements.filter(
        (element) => currentIds.has(element.id) && !initialIds.has(element.id),
      );

      const removed = allElements.filter(
        (element) => !currentIds.has(element.id) && initialIds.has(element.id),
      );

      return {
        newlySelected: added,
        newlyDeselected: removed,
      };
    }, [allElements, chosenElements, initialChosenElementsIds]);

    const toggleElement = (element: GenericElement) => {
        if (chosenElements.includes(element.id)) {
            setChosenElements(chosenElements.filter((id) => id !== element.id));
        } else {
            setChosenElements([...chosenElements, element.id]);
        }
    };

    const onClose = () => {
        setChosenElements(initialChosenElementsIds);
        popModal();
    };

    const handleSave = () => {
        onSave(allElements.filter((element) => chosenElements.includes(element.id)));
        popModal();
    }

    return (
      <>
        <div className="bg-white rounded-lg p-8 max-w-5xl w-full mx-4 animate-slideUp max-h-[90vh] flex flex-col">
          <h2 className="text-2xl font-bold mb-4 text-gray-800">
            {title}
          </h2>

          {/* Summary for Mobile */}
          {showSummary && (<div className="lg:hidden border border-gray-200 rounded-md bg-gray-50 mb-4">
            <button
              type="button"
              onClick={() => setIsMobileSummaryOpen((prev) => !prev)}
              className="w-full px-4 py-3 flex items-center justify-between text-left"
            >
              <span className="text-sm font-semibold text-gray-700">
                Resumo desta edição
              </span>
              <span className="text-xs font-medium text-gray-500">
                {isMobileSummaryOpen ? "Ocultar" : "Mostrar"}
              </span>
            </button>
            {isMobileSummaryOpen ? (
              <div className="px-4 pb-4">
                <EditSummary
                  newlySelected={newlySelected}
                  newlyDeselected={newlyDeselected}
                  className="max-h-56"
                />
              </div>
            ) : null}
          </div>)}


          {/* Search, Filter, and Results */}
          <div className={`grid grid-cols-1 ${(showSummary ? "lg:grid-cols-[2fr_1fr]" : "")} gap-6 flex-1 min-h-0`}>
            <div className="min-h-0 flex flex-col">
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Pesquisar ..."
                  className="w-full sm:w-auto flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
                <div className="flex gap-1 mt-2 sm:mt-0">
                  <button
                    type="button"
                    className={`px-3 py-1 rounded-md text-sm font-medium border transition-colors ${filterType === 'all' ? 'bg-teal-500 text-white border-teal-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'}`}
                    onClick={() => setFilterType('all')}
                  >
                    Todos
                  </button>
                  <button
                    type="button"
                    className={`px-3 py-1 rounded-md text-sm font-medium border transition-colors ${filterType === 'selected' ? 'bg-teal-500 text-white border-teal-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'}`}
                    onClick={() => setFilterType('selected')}
                  >
                    Selecionados
                  </button>
                  <button
                    type="button"
                    className={`px-3 py-1 rounded-md text-sm font-medium border transition-colors ${filterType === 'not_selected' ? 'bg-teal-500 text-white border-teal-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'}`}
                    onClick={() => setFilterType('not_selected')}
                  >
                    Não selecionados
                  </button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto space-y-2 mb-3 max-h-96 lg:max-h-none">
                {filteredElements.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">
                    {allElements.length === 0
                      ? "Nenhum elemento disponível"
                      : "Nenhum resultado para a pesquisa"}
                  </p>
                ) : (
                  filteredElements.map((element: GenericElement) => {
                    const isSelected = chosenElements.includes(element.id);
                    return (
                      <div
                        key={element.id}
                        onClick={() => toggleElement(element)}
                        className={`flex items-center justify-between px-4 py-3 rounded-md cursor-pointer transition-colors ${
                          isSelected
                            ? "bg-teal-50 border border-teal-300 hover:bg-teal-100"
                            : "bg-gray-50 hover:bg-gray-100"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0 ${
                              isSelected
                                ? "bg-teal-500 text-white"
                                : "bg-gray-200 text-gray-600"
                            }`}
                          >
                            {element.title.charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <p className="font-medium text-gray-800">
                              {element.title}
                            </p>
                            <p className="text-sm text-gray-500">
                              {element.subTitle}
                            </p>
                          </div>
                        </div>
                        {isSelected ? (
                          <svg
                            className="w-5 h-5 text-teal-600 flex-shrink-0"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                        ) : (
                          <svg
                            className="w-5 h-5 text-gray-400 flex-shrink-0"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M12 4v16m8-8H4"
                            />
                          </svg>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {showSummary && (<div className="hidden lg:flex border border-gray-200 rounded-md p-4 bg-gray-50 min-h-0 flex-col">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Resumo desta edição
              </h3>

              <EditSummary
                newlySelected={newlySelected}
                newlyDeselected={newlyDeselected}
              />
            </div>)}
          </div>

          {/* Count Message */}
          <p className="text-sm text-gray-500 mb-4">
            {chosenElements.length} elemento(s) selecionado(s)
          </p>

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
              onClick={handleSave}
              type="primary"
              flexible={true}
            >
              Salvar
            </Button>
          </div>
        </div>
      </>
    );
}

export default ChooseMultipleModal;
