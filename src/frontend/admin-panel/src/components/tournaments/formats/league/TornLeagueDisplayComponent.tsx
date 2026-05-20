interface LeagueFormatData {
    points_win: number;
    points_draw: number;
    points_loss: number;
    current_round: number;
}

const TornLeagueDisplayComponent = ({data} : {data: LeagueFormatData}) => {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <h3 className="font-semibold text-blue-900 mb-3">
          Formato: Liga (Pontos: {data.points_win} vitória, {data.points_draw} empate, {data.points_loss} derrota)
        </h3>
        <p className="text-sm text-blue-800 mb-4">
          Ronda atual: {data.current_round || 0}
        </p>
      </div>
    );
};

export default TornLeagueDisplayComponent;
