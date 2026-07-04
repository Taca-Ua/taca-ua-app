import TornLeagueMatchSugestionConfigModal from "./league/TornLeagueMatchSugestionConfigModal";

const GeneralFormatMatchesSuggestionsModal = ({format, tournamentId} : {format?: string, tournamentId: string}) => {

    if (format === 'league') {
        return <TornLeagueMatchSugestionConfigModal tournamentId={tournamentId}/>;
    }

    return null;
}

export default GeneralFormatMatchesSuggestionsModal;
