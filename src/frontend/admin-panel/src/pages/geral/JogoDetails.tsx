import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { useNotification } from '../../contexts/NotificationProvider';
import {
  matchesApi,
  type MatchDetail,
  type MatchUpdate,
  type MatchResultsUpdate,
  type ParticipantResult,
  type LineupDetail,
  type CommentDetail,
  type CommentCreate
} from '../../api/matches';

// ==================== Private Components ====================

// Match Header Component
const MatchHeader = ({ match }: { match: MatchDetail }) => {
  const getStatusBadge = (status: string) => {
    const statusConfig = {
      scheduled: { label: 'Agendado', color: 'bg-blue-100 text-blue-800' },
      in_progress: { label: 'Em Curso', color: 'bg-yellow-100 text-yellow-800' },
      finished: { label: 'Terminado', color: 'bg-green-100 text-green-800' },
      cancelled: { label: 'Cancelado', color: 'bg-red-100 text-red-800' },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.scheduled;

    return (
      <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };

  const participants = match.participants || [];

  const getName = (participant: typeof participants[0]) => {
    if (!participant) return 'TBD';
    return participant.team?.name || participant.athlete?.full_name || 'TBD';
  };

  const getScore = (participant: typeof participants[0]) => {
    return participant?.score ?? null;
  };

  const hasScores = match.status === 'finished' && participants.some(p => p.score !== null && p.score !== undefined);

  // For 2 participants, use traditional layout
  if (participants.length === 2) {
    return (
      <div className="bg-gradient-to-r from-teal-500 to-teal-600 text-white p-8">
        <div className="flex justify-between items-center gap-8 mb-4">
          <div className="flex-1 text-right">
            <h2 className="text-2xl font-bold">{getName(participants[0])}</h2>
          </div>

          <div className="flex-shrink-0 text-center">
            {hasScores ? (
              <div className="text-5xl font-bold">
                {getScore(participants[0])} - {getScore(participants[1])}
              </div>
            ) : (
              <div className="text-3xl font-bold opacity-75">VS</div>
            )}
          </div>

          <div className="flex-1">
            <h2 className="text-2xl font-bold">{getName(participants[1])}</h2>
          </div>
        </div>

        <div className="text-center">
          {getStatusBadge(match.status)}
        </div>
      </div>
    );
  }

  // For multiple participants, use grid layout
  return (
    <div className="bg-gradient-to-r from-teal-500 to-teal-600 text-white p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-center mb-4">Participantes</h2>
        <div className={`grid gap-4 ${participants.length === 3 ? 'grid-cols-3' : participants.length === 4 ? 'grid-cols-2 md:grid-cols-4' : 'grid-cols-2 md:grid-cols-3 lg:grid-cols-4'}`}>
          {participants.map((participant, index) => (
            <div key={participant.id} className="text-center p-4 bg-white bg-opacity-10 rounded-lg">
              <div className="text-lg font-bold mb-2">{getName(participant)}</div>
              {hasScores && (
                <div className="text-3xl font-bold">{getScore(participant) ?? '-'}</div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="text-center">
        {getStatusBadge(match.status)}
      </div>
    </div>
  );
};

// Match Info Component
const MatchInfo = ({
  match,
  isEditing,
  formData,
  setFormData,
  onSave,
  onCancel,
  saving
}: {
  match: MatchDetail;
  isEditing: boolean;
  formData: { location: string; startTime: string; status: string };
  setFormData: (data: any) => void;
  onSave: () => void;
  onCancel: () => void;
  saving: boolean;
}) => {
  const formatDateTime = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString('pt-PT', {
        dateStyle: 'long',
        timeStyle: 'short',
      });
    } catch {
      return dateString;
    }
  };

  if (!isEditing) {
    return (
      <div className="space-y-4">
        <div className="border-b pb-3">
          <label className="block text-sm font-medium text-gray-500 mb-1">Local</label>
          <p className="text-lg text-gray-800">{match.location}</p>
        </div>

        <div className="border-b pb-3">
          <label className="block text-sm font-medium text-gray-500 mb-1">Data e Hora</label>
          <p className="text-lg text-gray-800">{formatDateTime(match.start_time)}</p>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSave(); }} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Estado <span className="text-red-500">*</span>
        </label>
        <select
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          value={formData.status}
          onChange={(e) => setFormData({ ...formData, status: e.target.value })}
        >
          <option value="scheduled">Agendado</option>
          <option value="in_progress">Em Curso</option>
          <option value="finished">Terminado</option>
          <option value="cancelled">Cancelado</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Local <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          value={formData.location}
          onChange={(e) => setFormData({ ...formData, location: e.target.value })}
          placeholder="Ex: Campo Municipal"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Data e Hora <span className="text-red-500">*</span>
        </label>
        <input
          type="datetime-local"
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          value={formData.startTime}
          onChange={(e) => setFormData({ ...formData, startTime: e.target.value })}
          required
        />
      </div>

      <div className="flex gap-3 pt-4 border-t">
        <button
          type="button"
          onClick={onCancel}
          disabled={saving}
          className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md font-medium transition-colors disabled:opacity-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={saving}
          className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors disabled:opacity-50 flex items-center justify-center"
        >
          {saving ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              A Guardar...
            </>
          ) : (
            'Guardar'
          )}
        </button>
      </div>
    </form>
  );
};

// Results Section Component
const ResultsSection = ({
  match,
  onUpdate
}: {
  match: MatchDetail;
  onUpdate: () => void;
}) => {
  const [isEditingResults, setIsEditingResults] = useState(false);
  const [saving, setSaving] = useState(false);
  const [finalizing, setFinalizing] = useState(false);
  const { notify } = useNotification();
  const [results, setResults] = useState<{ [key: string]: { score: string; position: string } }>({});

  useEffect(() => {
    const initialResults: { [key: string]: { score: string; position: string } } = {};
    match.participants.forEach(p => {
      initialResults[p.id] = {
        score: p.score?.toString() || '',
        position: p.position?.toString() || '',
      };
    });
    setResults(initialResults);
  }, [match.participants]);

  const handleSaveResults = async () => {
    try {
      setSaving(true);

      const participant_results: ParticipantResult[] = match.participants.map(p => ({
        participant_id: p.id,
        score: results[p.id]?.score ? Number(results[p.id].score) : undefined,
        position: results[p.id]?.position ? Number(results[p.id].position) : undefined,
      }));

      const updateData: MatchResultsUpdate = {
        participant_results,
        // Do NOT auto-finish: status is not changed here
      };

      await matchesApi.updateMatchResults(match.id, updateData);
      setIsEditingResults(false);
      onUpdate();
    } catch (err) {
      console.error('Error updating results:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível guardar os resultados. Verifique os dados e tente novamente.', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleFinalizeMatch = async () => {
    if (!window.confirm('Tem a certeza que deseja finalizar este jogo? O estado será alterado para "Terminado".')) return;
    try {
      setFinalizing(true);
      await matchesApi.update(match.id, { status: 'finished' });
      onUpdate();
    } catch (err) {
      console.error('Error finalizing match:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível finalizar o jogo. Tente novamente.', 'error');
    } finally {
      setFinalizing(false);
    }
  };

  const getName = (participant: typeof match.participants[0]) => {
    return participant.team?.name || participant.athlete?.full_name || 'Participante';
  };

  const hasAnyResults = match.participants.some(p => p.score !== null && p.score !== undefined);

  if (match.status !== 'finished' && !isEditingResults) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-gray-800">Resultados</h3>
          <div className="flex gap-2">
            <button
              onClick={() => setIsEditingResults(true)}
              className="px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md text-sm font-medium transition-colors"
            >
              {hasAnyResults ? 'Editar Resultados' : 'Publicar Resultados'}
            </button>
            {hasAnyResults && (
              <button
                onClick={handleFinalizeMatch}
                disabled={finalizing}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm font-medium transition-colors disabled:opacity-50"
              >
                {finalizing ? 'A finalizar...' : 'Finalizar Jogo'}
              </button>
            )}
          </div>
        </div>
        {hasAnyResults ? (
          <div className="space-y-4">
            {match.participants.map((participant) => (
              <div key={participant.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <span className="font-semibold text-gray-800">{getName(participant)}</span>
                <div className="flex gap-6">
                  {participant.score !== null && participant.score !== undefined && (
                    <div className="text-right">
                      <div className="text-sm text-gray-500">Pontuação</div>
                      <div className="text-2xl font-bold text-teal-600">{participant.score}</div>
                    </div>
                  )}
                  {participant.position !== null && participant.position !== undefined && (
                    <div className="text-right">
                      <div className="text-sm text-gray-500">Posição</div>
                      <div className="text-2xl font-bold text-teal-600">{participant.position}º</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">Os resultados ainda não foram publicados.</p>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-gray-800">Resultados</h3>
        {!isEditingResults && match.status === 'finished' && (
          <button
            onClick={() => setIsEditingResults(true)}
            className="px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md text-sm font-medium transition-colors"
          >
            Editar Resultados
          </button>
        )}
      </div>

      {!isEditingResults ? (
        <div className="space-y-4">
          {match.participants.map((participant) => (
            <div key={participant.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
              <span className="font-semibold text-gray-800">{getName(participant)}</span>
              <div className="flex gap-6">
                {participant.score !== null && participant.score !== undefined && (
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Pontuação</div>
                    <div className="text-2xl font-bold text-teal-600">{participant.score}</div>
                  </div>
                )}
                {participant.position !== null && participant.position !== undefined && (
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Posição</div>
                    <div className="text-2xl font-bold text-teal-600">{participant.position}º</div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {match.participants.map((participant) => (
            <div key={participant.id} className="p-4 bg-gray-50 rounded-lg">
              <div className="font-semibold text-gray-800 mb-3">{getName(participant)}</div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Pontuação</label>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                    value={results[participant.id]?.score || ''}
                    onChange={(e) => setResults({
                      ...results,
                      [participant.id]: { ...results[participant.id], score: e.target.value }
                    })}
                    placeholder="0"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Posição</label>
                  <input
                    type="number"
                    min="1"
                    step="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                    value={results[participant.id]?.position || ''}
                    onChange={(e) => setResults({
                      ...results,
                      [participant.id]: { ...results[participant.id], position: e.target.value }
                    })}
                    placeholder="1"
                  />
                </div>
              </div>
            </div>
          ))}

          <div className="flex gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={() => {
                setIsEditingResults(false);
              }}
              disabled={saving}
              className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md font-medium transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              onClick={handleSaveResults}
              disabled={saving}
              className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors disabled:opacity-50"
            >
              {saving ? 'A Guardar...' : 'Guardar Resultados'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Lineups Section Component
const LineupsSection = ({ match }: { match: MatchDetail }) => {
  const [lineups, setLineups] = useState<LineupDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();

  useEffect(() => {
    fetchLineups();
  }, [match.id]);

  const fetchLineups = async () => {
    try {
      setLoading(true);
      const data = await matchesApi.getLineups(match.id);
      setLineups(data);
    } catch (err) {
      console.error('Error loading lineups:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível carregar as convocatórias. Tente recarregar a página.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadTeamSheet = async (teamId: string) => {
    try {
      const blob = await matchesApi.getMatchTeamSheet(match.id, teamId);
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
      setTimeout(() => window.URL.revokeObjectURL(url), 10000);
    } catch (err) {
      console.error('Error downloading team sheet:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível descarregar a ficha de equipa. Tente novamente.', 'error');
    }
  };

  // Create a map of team_id to team object from match participants
  const teamMap = match.participants.reduce((acc, participant) => {
    if (participant.team) {
      acc[participant.team.id] = participant.team;
    }
    return acc;
  }, {} as { [key: string]: typeof match.participants[0]['team'] });

  // Group lineups by team
  const lineupsByTeam = lineups.reduce((acc, lineup) => {
    if (!acc[lineup.team_id]) {
      acc[lineup.team_id] = [];
    }
    acc[lineup.team_id].push(lineup);
    return acc;
  }, {} as { [key: string]: LineupDetail[] });

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Convocatórias</h3>

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
        </div>
      ) : lineups.length === 0 ? (
        <p className="text-gray-600">Nenhuma convocatória definida.</p>
      ) : (
        <div className="space-y-6">
          {Object.entries(lineupsByTeam).map(([teamId, teamLineups]) => {
            const starters = teamLineups.filter(l => l.is_starter);
            const bench = teamLineups.filter(l => !l.is_starter);
            const team = teamMap[teamId];

            return (
              <div key={teamId} className="border-l-4 border-teal-500 pl-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-semibold text-lg text-gray-800">
                    {team?.name || `Equipa ${teamId.substring(0, 8)}`}
                  </h4>
                  <button
                    onClick={() => handleDownloadTeamSheet(teamId)}
                    className="px-3 py-1.5 bg-orange-500 hover:bg-orange-600 text-white rounded-md text-sm font-medium transition-colors flex items-center gap-1"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Ficha de Equipa
                  </button>
                </div>

                {starters.length > 0 && (
                  <div className="mb-3">
                    <p className="text-sm font-medium text-gray-600 mb-2">Titulares</p>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {starters.map(lineup => (
                        <div key={lineup.id} className="flex items-center gap-2 p-2 bg-teal-50 rounded">
                          <span className="flex-shrink-0 w-8 h-8 bg-teal-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                            {lineup.jersey_number}
                          </span>
                          <span className="text-sm text-gray-800 truncate">
                            {lineup.player?.full_name || 'Jogador'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {bench.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-2">Suplentes</p>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {bench.map(lineup => (
                        <div key={lineup.id} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                          <span className="flex-shrink-0 w-8 h-8 bg-gray-400 text-white rounded-full flex items-center justify-center text-sm font-bold">
                            {lineup.jersey_number}
                          </span>
                          <span className="text-sm text-gray-800 truncate">
                            {lineup.player?.full_name || 'Jogador'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// Comments Section Component
const CommentsSection = ({ matchId }: { matchId: string }) => {
  const [comments, setComments] = useState<CommentDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();
  const [newComment, setNewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchComments();
  }, [matchId]);

  const fetchComments = async () => {
    try {
      setLoading(true);
      const data = await matchesApi.getComments(matchId);
      setComments(data);
    } catch (err) {
      console.error('Error loading comments:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível carregar os comentários. Tente recarregar a página.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    try {
      setSubmitting(true);
      const commentData: CommentCreate = { message: newComment.trim() };
      const addedComment = await matchesApi.addComment(matchId, commentData);
      setComments([...comments, addedComment]);
      setNewComment('');
    } catch (err) {
      console.error('Error adding comment:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível adicionar o comentário. Tente novamente.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    if (!confirm('Tem a certeza que deseja eliminar este comentário?')) return;

    try {
      await matchesApi.deleteComment(matchId, commentId);
      setComments(comments.filter(c => c.id !== commentId));
    } catch (err) {
      console.error('Error deleting comment:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível eliminar o comentário. Tente novamente.', 'error');
    }
  };

  const formatCommentDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString('pt-PT', {
        dateStyle: 'short',
        timeStyle: 'short',
      });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Comentários</h3>

      <div className="mb-6">
        <textarea
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent resize-none"
          rows={3}
          placeholder="Adicionar um comentário..."
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
        ></textarea>
        <button
          onClick={handleAddComment}
          disabled={submitting || !newComment.trim()}
          className="mt-2 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? 'A Adicionar...' : 'Adicionar Comentário'}
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
        </div>
      ) : comments.length === 0 ? (
        <p className="text-gray-600 text-center py-4">Nenhum comentário ainda.</p>
      ) : (
        <div className="space-y-4">
          {comments.map((comment) => (
            <div key={comment.id} className="p-4 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-teal-500 text-white rounded-full flex items-center justify-center font-bold text-sm">
                    {comment.created_by.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-semibold text-sm text-gray-800">{comment.created_by}</p>
                    <p className="text-xs text-gray-500">{formatCommentDate(comment.created_at)}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteComment(comment.id)}
                  className="text-red-600 hover:text-red-700 p-1"
                  title="Eliminar comentário"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
              <p className="text-gray-700 whitespace-pre-wrap">{comment.message}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Delete Modal Component
const DeleteModal = ({
  show,
  onClose,
  onConfirm
}: {
  show: boolean;
  onClose: () => void;
  onConfirm: () => void;
}) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 animate-fade-in">
        <div className="flex items-center mb-4">
          <div className="flex-shrink-0 w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mr-4">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-gray-900">Confirmar Eliminação</h3>
        </div>

        <p className="text-gray-600 mb-6">
          Tem a certeza que deseja eliminar este jogo? Esta ação não pode ser revertida e todos os dados associados serão permanentemente removidos.
        </p>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md font-medium transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium transition-colors"
          >
            Sim, Eliminar
          </button>
        </div>
      </div>
    </div>
  );
};

// ==================== Main Component ====================

const JogoDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [match, setMatch] = useState<MatchDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();
  const [saving, setSaving] = useState(false);

  // Edit mode state
  const [isEditingInfo, setIsEditingInfo] = useState(false);
  const [formData, setFormData] = useState({
    location: '',
    startTime: '',
    status: 'scheduled' as 'scheduled' | 'in_progress' | 'finished' | 'cancelled',
  });

  // Delete confirmation
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const fetchMatch = async () => {
    if (!id) return;

    try {
      setLoading(true);
      const matchData = await matchesApi.getById(id);
      setMatch(matchData);

      // Initialize form data
      setFormData({
        location: matchData.location,
        startTime: toInputDateTime(matchData.start_time),
        status: matchData.status,
      });
    } catch (err) {
      console.error('Error loading match:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível carregar os dados do jogo. Tente recarregar a página.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMatch();
  }, [id]);

  const toInputDateTime = (dateString: string | undefined | null) => {
    if (!dateString) return '';
    const d = new Date(dateString);
    if (Number.isNaN(d.getTime())) return '';
    const pad = (n: number) => n.toString().padStart(2, '0');
    const year = d.getFullYear();
    const month = pad(d.getMonth() + 1);
    const day = pad(d.getDate());
    const hours = pad(d.getHours());
    const minutes = pad(d.getMinutes());
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  const handleSaveInfo = async () => {
    if (!match) return;

    if (!formData.location.trim()) {
      notify('O local é obrigatório', 'error');
      return;
    }

    if (!formData.startTime.trim()) {
      notify('A data e hora são obrigatórias', 'error');
      return;
    }

    try {
      setSaving(true);

      const updateData: MatchUpdate = {
        location: formData.location.trim(),
        start_time: new Date(formData.startTime).toISOString(),
        status: formData.status,
      };

      const updatedMatch = await matchesApi.update(match.id, updateData);
      setMatch(updatedMatch);
      setIsEditingInfo(false);

      // Update form data with the response
      setFormData({
        location: updatedMatch.location,
        startTime: toInputDateTime(updatedMatch.start_time),
        status: updatedMatch.status,
      });
    } catch (err) {
      console.error('Error updating match:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível guardar as alterações ao jogo. Tente novamente.', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleCancelEdit = () => {
    if (!match) return;

    setFormData({
      location: match.location,
      startTime: toInputDateTime(match.start_time),
      status: match.status,
    });
    setIsEditingInfo(false);
  };

  const handleDelete = async () => {
    if (!match) return;

    try {
      await matchesApi.delete(match.id);
      navigate(`/geral/torneios/${match.tournament_id}`);
    } catch (err) {
      console.error('Error deleting match:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível eliminar o jogo. Poderá ter resultados ou convocatórias registadas.', 'error');
      setShowDeleteModal(false);
    }
  };

  const handleDownloadSheet = async () => {
    if (!match) return;

    try {
        const blob = await matchesApi.getMatchSheet(match.id);
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank');
        // Optionally revoke after some time
        setTimeout(() => window.URL.revokeObjectURL(url), 10000);
    } catch (err) {
        console.error('Error downloading match sheet:', err);
        notify(err instanceof Error ? err.message : 'Não foi possível descarregar a ficha de jogo. Tente novamente.', 'error');
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      </div>
    );
  }

  if (!match) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 p-8 max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="text-6xl mb-4">⚽</div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Jogo não encontrado</h2>
            <p className="text-gray-600 mb-6">O jogo que procura não existe ou foi removido.</p>
            <button
              onClick={() => navigate('/geral/dashboard')}
              className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
            >
              Voltar ao Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 p-8 max-w-6xl mx-auto">
        <button
          onClick={() => navigate(-1)}
          className="mb-6 flex items-center text-teal-600 hover:text-teal-700 font-medium transition-colors group"
        >
          <svg
            className="w-5 h-5 mr-2 transform group-hover:-translate-x-1 transition-transform"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Voltar
        </button>

        <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
          <MatchHeader match={match} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-gray-800">Informações</h3>
                {!isEditingInfo && (
                  <button
                    onClick={() => setIsEditingInfo(true)}
                    className="text-teal-600 hover:text-teal-700 p-1"
                    title="Editar"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                )}
              </div>

              <MatchInfo
                match={match}
                isEditing={isEditingInfo}
                formData={formData}
                setFormData={setFormData}
                onSave={handleSaveInfo}
                onCancel={handleCancelEdit}
                saving={saving}
              />
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Ações</h3>
              <div className="space-y-3">
                <button
                  onClick={handleDownloadSheet}
                  className="w-full px-4 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-md font-medium transition-colors flex items-center justify-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Baixar Ficha de Jogo
                </button>

                <button
                  onClick={() => setShowDeleteModal(true)}
                  className="w-full px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium transition-colors flex items-center justify-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Eliminar Jogo
                </button>
              </div>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            <ResultsSection match={match} onUpdate={fetchMatch} />
            <LineupsSection match={match} />
            <CommentsSection matchId={match.id} />
          </div>
        </div>
      </div>

      <DeleteModal
        show={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleDelete}
      />
    </div>
  );
};

export default JogoDetails;
