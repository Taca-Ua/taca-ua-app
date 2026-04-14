import { type TournamentDetail } from "../../api/tournaments"

const TournamentFinishModal = ( {
    controller,
    tournamentId,
    onSave,
} : {
    controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>],
    tournamentId: string,
    onSave: (updatedTournament: TournamentDetail) => void
} ) => {
    const [isOpen, setIsOpen] = controller;

    if ( !isOpen ) return null;
}

export default TournamentFinishModal
