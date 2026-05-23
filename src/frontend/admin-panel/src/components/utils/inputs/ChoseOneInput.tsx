import { useState } from "react";
import ChoseOneModal from "../costum_menus/ChoseOneModal";
import { useModal } from "../../../contexts/ModalContext";

interface GenericElement {
    id: string;
    title: string;
    subTitle?: string;
}

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

    return (
      <div>
        <div
          onClick={() =>
            pushModal(
              <ChoseOneModal
                allElementsLoader={allElementsLoader}
                onSelect={(element) => {
                  onSelect(element);
                  setElement(element);
                }}
                initialSelectedId={element ? element.id : initialElement?.id || undefined}
              />,
            )
          }
          className="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 cursor-pointer"
        >
          {element ? element.title : "Selecionar Elemento"}
        </div>
      </div>
    );
}

export default ChoseOneInput;
