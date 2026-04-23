import { useState } from "react";
import ChoseOneModal from "../costum_menus/ChoseOneModal";
import { useModal } from "../../../contexts/ModalContext";

const ChoseOneInput = ( {
    allElementsLoader,
    onSelect
} : {
    allElementsLoader: () => Promise<{ id: string, title: string, subTitle?: string }[]>
    onSelect: (element: { id: string, title: string, subTitle?: string } | null) => void
} ) => {
    const { pushModal } = useModal();

    const [element, setElement] = useState<{ id: string, title: string, subTitle?: string } | null>(null)

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
