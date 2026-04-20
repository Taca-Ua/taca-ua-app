import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ConfirmModal from '../../components/ConfirmModal';
import { useNotification } from '../../contexts/NotificationProvider';
import { btn } from '../../styles/buttonStyles';
import {
  matchesApi,
  type MatchDetail,
  type CommentCreate
} from '../../api/matches';
import MatchInfoComponent from '../../components/matches/MatchInfoComponent';
import MatchResultsComponent from '../../components/matches/MatchesResultsComponent';

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
    return participant.name || 'TBD';
  };

  const getScore = (participant: typeof participants[0]) => {
    return participant.score ?? null;
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
            <div key={index} className="text-center p-4 bg-white bg-opacity-10 rounded-lg">
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

// Lineups Section Component
const LineupsSection = ({ match }: { match: MatchDetail }) => {
  const { notify } = useNotification();

  const getParticipantName = (participant_id: string) => {
    const participant = match.participants.find(p => p.id === participant_id);
    return participant ? participant.name : 'Participante';
  };

  const handleDownloadTeamSheet = async (teamId: string) => {
    try {
        const blob = await matchesApi.getMatchTeamSheet(match.id, teamId);
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank');
        // Optionally revoke after some time
        setTimeout(() => window.URL.revokeObjectURL(url), 10000);
    } catch (err) {
        console.error('Error downloading team sheet:', err);
        notify(err instanceof Error ? err.message : 'Não foi possível descarregar a ficha de equipa. Tente novamente.', 'error');
    }
  };

  if (match.lineups === null || match.lineups === undefined) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Convocatórias</h3>
        <p className="text-gray-600">Dados de convocatória não disponíveis.</p>
      </div>
    );
  }

  if (match.lineups?.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Convocatórias</h3>
        <p className="text-gray-600">Nenhuma convocatória definida.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Convocatórias</h3>

      <div className="space-y-6">
          {match.lineups.map((participant) => {
            const starters = participant.lineup.filter(l => l.is_starter);
            const bench = participant.lineup.filter(l => !l.is_starter);

            return (
              <div key={participant.participant_id} className="border-l-4 border-teal-500 pl-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-semibold text-lg text-gray-800">
                    {getParticipantName(participant.participant_id)}
                  </h4>
                  <button
                    onClick={() => handleDownloadTeamSheet(participant.participant_id)}
                    className="px-3 py-1.5 bg-orange-500 hover:bg-orange-600 text-white rounded-md text-sm font-medium transition-colors flex items-center gap-1"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                    Ficha de Equipa
                  </button>
                </div>

                {starters.length > 0 && (
                  <div className="mb-3">
                    <p className="text-sm font-medium text-gray-600 mb-2">
                      Titulares
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {starters.map((lineup) => (
                        <div
                          key={lineup.player_id}
                          className="flex items-center gap-2 p-2 bg-teal-50 rounded"
                        >
                          <span className="flex-shrink-0 w-8 h-8 bg-teal-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                            {lineup.jersey_number}
                          </span>
                          <span className="text-sm text-gray-800 truncate">
                            {lineup.name || "Jogador"}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {bench.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-2">
                      Suplentes
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {bench.map((lineup) => (
                        <div
                          key={lineup.player_id}
                          className="flex items-center gap-2 p-2 bg-gray-50 rounded"
                        >
                          <span className="flex-shrink-0 w-8 h-8 bg-gray-400 text-white rounded-full flex items-center justify-center text-sm font-bold">
                            {lineup.jersey_number}
                          </span>
                          <span className="text-sm text-gray-800 truncate">
                            {lineup.name || "Jogador"}
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
    </div>
  );
};

// Comments Section Component
const CommentsSection = ({ match }: { match: MatchDetail }) => {
  const [comments, setComments] = useState<typeof match.comments[0][]>([... (match.comments || [])]);
  const { notify } = useNotification();
  const [newComment, setNewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [commentToDelete, setCommentToDelete] = useState<string | null>(null);
  const [deletingComment, setDeletingComment] = useState(false);

  // const comments = match.comments || [];

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    try {
      setSubmitting(true);
      const commentData: CommentCreate = { message: newComment.trim() };
      let updatedMatch = await matchesApi.addComment(match.id, commentData);
      setNewComment('');
      setComments([ ...updatedMatch.comments ]);
    } catch (err) {
      console.error('Error adding comment:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível adicionar o comentário. Tente novamente.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteComment = (commentId: string) => {
    setCommentToDelete(commentId);
  };

  const confirmDeleteComment = async () => {
    if (!commentToDelete) return;

    try {
      setDeletingComment(true);
      console.log('Deleting comment with ID:', commentToDelete);
      await matchesApi.deleteComment(match.id, commentToDelete);
      setCommentToDelete(null);
      setComments(prev => prev.filter(c => c.id !== commentToDelete));
    } catch (err) {
      console.error('Error deleting comment:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível eliminar o comentário. Tente novamente.', 'error');
    } finally {
      setDeletingComment(false);
    }
  };

  const renderCommentListArea = () => {
    if (comments.length === 0) {
      return <p className="text-gray-600 text-center py-4">Nenhum comentário ainda.</p>;
    }

    return (
      <div className="space-y-4">
        {comments.map((comment) => (
          <div key={comment.id} className="p-4 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-start mb-2">
              {/* <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-teal-500 text-white rounded-full flex items-center justify-center font-bold text-sm">
                  {comment.created_by.charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="font-semibold text-sm text-gray-800">
                    {comment.created_by}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatCommentDate(comment.created_at)}
                  </p>
                </div>
              </div> */}
              <button
                onClick={() => handleDeleteComment(comment.id)}
                className="text-red-600 hover:text-red-700 p-1"
                title="Eliminar comentário"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            </div>
            <p className="text-gray-700 whitespace-pre-wrap">
              {comment.message}
            </p>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Comentários</h3>

      {/* Comment Input */}
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
          className={`mt-2 px-4 py-2 ${btn.primary} rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {submitting ? 'A Adicionar...' : 'Adicionar Comentário'}
        </button>
      </div>

      {/* Comments List */}
      {renderCommentListArea()}

      <ConfirmModal
        isOpen={commentToDelete !== null}
        title="Eliminar comentário"
        message="Tem a certeza que deseja eliminar este comentário?"
        confirmLabel="Eliminar"
        variant="danger"
        loading={deletingComment}
        onCancel={() => {
          if (!deletingComment) {
            setCommentToDelete(null);
          }
        }}
        onConfirm={confirmDeleteComment}
      />
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

  // Delete confirmation
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const fetchMatch = async () => {
    if (!id) return;

    try {
      setLoading(true);
      const matchData = await matchesApi.getById(id);
      setMatch(matchData);
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
      <div className="flex-1 flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  if (!match) {
    return (
        <div className="flex-1 p-8 max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="text-6xl mb-4">⚽</div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Jogo não encontrado</h2>
            <p className="text-gray-600 mb-6">O jogo que procura não existe ou foi removido.</p>
            <button
              onClick={() => navigate('/dashboard')}
              className={`px-6 py-3 ${btn.primary} rounded-md font-medium transition-colors`}
            >
              Voltar ao Dashboard
            </button>
          </div>
        </div>
    );
  }

  return (
      <div className="flex-1 p-8 max-w-6xl mx-auto">
        <div className="mb-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Detalhes do Jogo</h1>
          <button
            onClick={() => navigate(`/geral/torneios/${match.tournament_id}`)}
            className={`px-6 py-3 ${btn.secondary} rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400`}
          >
            Voltar
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
          <MatchHeader match={match} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-6">
            <MatchInfoComponent
              match={match}
              onMatchUpdated={(updatedMatch) => setMatch(updatedMatch)}
            />

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Ações</h3>
              <div className="space-y-3">
                <button
                  onClick={handleDownloadSheet}
                  className={`w-full px-4 py-3 ${btn.info} rounded-md font-medium transition-colors flex items-center justify-center`}
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Baixar Ficha de Jogo
                </button>

                <button
                  onClick={() => setShowDeleteModal(true)}
                  className={`w-full px-4 py-3 ${btn.danger} rounded-md font-medium transition-colors flex items-center justify-center`}
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
            <MatchResultsComponent matchState={[match, setMatch]} />
            <LineupsSection match={match} />
            <CommentsSection match={match} />
          </div>
        </div>

        <ConfirmModal
          isOpen={showDeleteModal}
          title="Eliminar jogo"
          message="Tem a certeza que deseja eliminar este jogo? Esta ação não pode ser revertida e todos os dados associados serão permanentemente removidos."
          confirmLabel="Sim, Eliminar"
          variant="danger"
          onCancel={() => setShowDeleteModal(false)}
          onConfirm={handleDelete}
        />
      </div>
  );
};

export default JogoDetails;
