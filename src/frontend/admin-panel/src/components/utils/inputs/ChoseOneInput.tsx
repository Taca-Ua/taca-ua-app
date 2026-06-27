import { useState } from "react";
import ChoseOneModal from "../costum_menus/ChoseOneModal";
import { type GenericElement } from "../costum_menus/ChoseOneModal";
import { useModal } from "../../../contexts/ModalContext";


const ChoseOneInput = ( {
    allElementsLoader,
    onSelect,
    elementState,
    initialElement,
} : {
    elementState?: [GenericElement | null, React.Dispatch<React.SetStateAction<GenericElement | null>>]
    allElementsLoader: () => Promise<GenericElement[]>
    onSelect: (element: GenericElement | null) => void
    initialElement?: GenericElement | null
} ) => {
    const { pushModal } = useModal();

    const [element, setElement] = elementState || useState<GenericElement | null>(initialElement || null);

    const handleClick = () => {
        pushModal(
            <ChoseOneModal
                allElementsLoader={allElementsLoader}
                onSelect={(element) => {
                    onSelect(element);
                    setElement(element);
                }}
                initialSelectedId={element ? element.id : initialElement?.id || undefined}
            />,
        );
    }

    return (
      <div
        onClick={handleClick}
        className="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 cursor-pointer"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            handleClick();
          }
        }}
      >
        {element ? element.title : "Selecionar Elemento"}
      </div>
    );
}

export default ChoseOneInput;
