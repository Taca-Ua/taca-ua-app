import { useEffect, useState } from "react"
import { matchesApi, type MatchListItem } from "../../api/matches"

const MatchesListComponent = ( {
    tournamentId
} : {
    tournamentId: string
} ) => {

    const [matches, setMatches] = useState<MatchListItem[]>([]);
    const [loading, setLoading] = useState<boolean>( true );

    useEffect( () => {
        const fetchMatches = async () => {
            setLoading( true );
            try {
                const response = await matchesApi.getAll( {
                    tournament_id: tournamentId
                } );
                setMatches( response );
            } catch ( error ) {
                console.error( "Error fetching matches:", error );
            } finally {
                setLoading( false );
            }
        };
        fetchMatches();
    }, [ tournamentId ] );

    if ( loading ) {
        return <div>Loading matches...</div>;
    }

    return (
        <div>
            <h2>Matches List</h2>
            <ul>
                {matches.map( ( match ) => (
                    <li key={match.id}>
                        Match ID: {match.id}, Players: {match.participants.map( ( p ) => p.name ).join( " vs " )}, Status: {match.status}
                    </li>
                ) )}
            </ul>
        </div>
    );
}

export default MatchesListComponent
