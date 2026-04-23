import React, { createContext, useContext, useEffect, useState } from "react";

type ModalContextType = {
  modals: React.ReactNode[];
  pushModal: (component: React.ReactNode) => void;
  popModal: () => void;
  clearModals: () => void;
};

const ModalContext = createContext<ModalContextType | null>(null);

export const useModal = () => useContext(ModalContext)!;

const ModalStack = () => {
  const { modals, popModal } = useModal();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        popModal();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [popModal]);

  if (modals.length === 0) return null;

  return (
    <div className="fixed inset-0 pointer-events-none bg-black/50 flex items-center justify-center">
      {modals.map((modal, index) => {
        const offset = (modals.length - 1 - index) * 200;

        return (
          <div
            key={index}
            className="absolute inset-0 flex items-center justify-center transition-all duration-300 animate-slideUp"
            style={{
              transform: `translateX(-${offset}px) scale(${modals.length - index === 1 ? 1 : 0.95})`,
              zIndex: index,
              pointerEvents: index === modals.length - 1 ? "auto" : "none",
              filter: `blur(${(modals.length - 1 - index) * 2}px)`,
            }}
          >
            {modal}
          </div>
        );
      })}
    </div>
  );
};

export const ModalProvider = ({ children }: { children: React.ReactNode }) => {
  const [modals, setModals] = useState<React.ReactNode[]>([]);

  const pushModal = (component: React.ReactNode) => {
    if (component === null) return;
    setModals((prev) => [...prev, component]);
  }

  const popModal = () => {
    setModals((prev) => prev.slice(0, -1));
  };

  const clearModals = () => {
    setModals([]);
  };

  return (
    <ModalContext.Provider value={{ modals, pushModal, popModal, clearModals }}>
      {children}
      <ModalStack />
    </ModalContext.Provider>
  );
};
