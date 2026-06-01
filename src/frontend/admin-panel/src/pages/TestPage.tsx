import { useEffect } from "react";
import Button from "../components/utils/Button";
import { useModal } from "../contexts/ModalContext";
import MatchesCalendarComponent from "../components/matches/MatchesCalendarComponent";

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
    <div className="w-2/3">
      <MatchesCalendarComponent />
    </div>
  );
};

export default TestPage;
