import { useState } from "react";
import ChoseOneModal from "../costum_menus/ChoseOneModal";

const ChoseOneInput = ( {
    allElementsLoader,
    onSelect
} : {
    allElementsLoader: () => Promise<{ id: string, title: string, subTitle?: string }[]>
    onSelect: (element: { id: string, title: string, subTitle?: string } | null) => void
} ) => {

    const [choseModalOpen, setChoseModalOpen] = useState(false)
    const [element, setElement] = useState<{ id: string, title: string, subTitle?: string } | null>(null)

    return (
      <div>
        <div
          onClick={() => setChoseModalOpen(true)}
          className="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 cursor-pointer"
        >
            {element ? element.title : "Selecionar Elemento"}
        </div>

        <ChoseOneModal
          controller={[choseModalOpen, setChoseModalOpen]}
          allElementsLoader={allElementsLoader}
          onSelect={(element) => {
            onSelect(element);
            setElement(element);
            setChoseModalOpen(false);
          }}
        />
      </div>
    );
}

export default ChoseOneInput;
