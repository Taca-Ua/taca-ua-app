import TornLeagueMetaInput from "./league/TornLeagueMetaInput";

const GeneralFormatMetaInput = ({format, data} : {format: string, data: Record<string, unknown>}) => {
    if (format === 'league') {
        return <TornLeagueMetaInput data={data}/>
    }

    return null;
}

export default GeneralFormatMetaInput;
