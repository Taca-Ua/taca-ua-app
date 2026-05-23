import React, { createContext, useContext, useEffect, useState } from "react";
import Button from "../components/utils/Button";
import { useModal } from "../contexts/ModalContext";

const Example = () => {
  const { popModal, pushModal } = useModal();

  useEffect(() => {
    console.log("Mounting example modal");
  }, []);

  return (
    <div className="bg-white p-6 rounded-xl shadow-xl">
      <Button
        onClick={() =>
          pushModal(<Example />)
        }
      >
        Open Modal
      </Button>
      <Button onClick={popModal} type="secondary">
        Close Modal
      </Button>
    </div>
  );
};

const TestPage = () => {
  return (
    // <></>
    <Example />
  );
};

export default TestPage;
