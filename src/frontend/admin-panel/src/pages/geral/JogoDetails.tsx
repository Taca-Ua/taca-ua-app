import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useNotification } from '../../contexts/NotificationProvider';
import {
  matchesApi,
  type MatchDetail,
  type CommentCreate
} from '../../api/matches';
import MatchInfoComponent from '../../components/matches/MatchInfoComponent';
import MatchResultsComponent from '../../components/matches/MatchesResultsComponent';
import Button from '../../components/utils/Button';
import { useModal } from '../../contexts/ModalContext';
import MatchTeamLineupModal from '../../components/matches/MatchTeamLineupModal';
import { useAuth } from '../../hooks/useAuth';
import { navigateBack } from '../../utils';
import LazyImage from '../../components/utils/LazyImage';

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

          {participants[0].logo_url ? (
            <LazyImage
              src={participants[0].logo_url}
              alt={getName(participants[0])}
              className="w-24 h-24 object-cover rounded-full mx-auto mb-2"
            />
          ) : null}

          <div className="flex-shrink-0 text-center">
            {hasScores ? (
              <div className="text-5xl font-bold">
                {getScore(participants[0])} - {getScore(participants[1])}
              </div>
            ) : (
              <div className="text-3xl font-bold opacity-75">VS</div>
            )}
          </div>

          {participants[1].logo_url ? (
            <LazyImage
              src={participants[1].logo_url}
              alt={getName(participants[1])}
              className="w-24 h-24 object-cover rounded-full mx-auto mb-2"
            />
          ) : null}

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
              { participant.logo_url ? (
                <LazyImage
                  src={participant.logo_url}
                  alt={getName(participant)}
                  className="w-16 h-16 object-cover mx-auto mb-2"
                />
              ) : null }
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
const LineupsSection = ({ matchState }: { matchState: [MatchDetail, React.Dispatch<React.SetStateAction<MatchDetail | null>>] }) => {
  const { pushModal } = useModal();
  const [match,] = matchState;

  const getParticipantName = (participant_id: string) => {
    const participant = match.participants.find(p => p.id === participant_id);
    return participant ? participant.name : 'Participante';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Convocatórias</h3>

      <div className="space-y-6">
          {match.participants.map((participant) => {

            return (
              <div key={participant.id} className="border-l-4 border-teal-500 pl-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-semibold text-lg text-gray-800">
                    {getParticipantName(participant.id)}
                  </h4>
                  <Button
                    onClick={() => {pushModal(
                      <MatchTeamLineupModal matchId={match.id} participantId={participant.id} />
                    )}}
                    type='info'
                    padding='px-10 py-2'
                    active={participant.can_edit}
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </Button>
                </div>
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
      notify('Não foi possível adicionar o comentário. Tente novamente.', 'error');
    } finally {
      setSubmitting(false);
    }
  };
  const handleDeleteComment = async (commentId: string) => {
    matchesApi.deleteComment(match.id, commentId).then(() => {
      setComments(prev => prev.filter(c => c.id !== commentId));
    }).catch(err => {
      console.error('Error deleting comment:', err);
      notify('Não foi possível eliminar o comentário. Tente novamente.', 'error');
    });
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
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-teal-500 text-white rounded-full flex items-center justify-center font-bold text-sm">
                  {comment.author_name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="font-semibold text-sm text-gray-800">
                    {comment.author_name}
                  </p>
                  {/* <p className="text-xs text-gray-500">
                    {formatCommentDate(comment.created_at)}
                  </p> */}
                </div>
              </div>
              <div />
              <Button
                onClick={() => handleDeleteComment(comment.id)}
                type="danger"
                active={comment.can_edit}
                confirmation={{
                  title: "Eliminar comentário",
                  message: "Tem a certeza que deseja eliminar este comentário?",
                  confirmLabel: "Eliminar",
                }}
                padding="px-2 py-2"
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
              </Button>
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
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Comentários</h3>
        <div className='flex gap-4 mb-4'>
          <Button
            onClick={handleAddComment}
            type='primary'
            disabled={submitting || !newComment.trim()}
          >
            {submitting ? 'A Adicionar...' : 'Adicionar Comentário'}
          </Button>
        </div>
      </div>

      {/* Comment Input */}
      <div className="mb-6">
        <textarea
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent resize-none"
          rows={3}
          placeholder="Adicionar um comentário..."
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
        ></textarea>
      </div>

      {/* Comments List */}
      {renderCommentListArea()}
    </div>
  );
};

// ==================== Main Component ====================

const JogoDetails = () => {
  const { id } = useParams<{ id: string }>();

  const [match, setMatch] = useState<MatchDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();
  const { isAdminGeneral } = useAuth();
  const navigate  = useNavigate();

  const handleBack = () => {
    navigateBack(navigate, `/torneios/${match?.tournament.id || ''}`);
  };

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
      handleBack();
    } catch (err) {
      console.error('Error deleting match:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível eliminar o jogo. Poderá ter resultados ou convocatórias registadas.', 'error');
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

  const handleActivateMatch = () => {
    if (!match) return;

    matchesApi.update(match.id, { status: 'in_progress' }).then((updatedMatch) => {
      setMatch(updatedMatch);
      notify('O jogo foi ativado com sucesso.', 'success');
    }).catch(err => {
      console.error('Error activating match:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível ativar o jogo. Tente novamente.', 'error');
    });
  }

  const handleFinishMatch = () => {
    if (!match) return;

    matchesApi.update(match.id, { status: 'finished' }).then((updatedMatch) => {
      setMatch(updatedMatch);
      notify('O jogo foi terminado com sucesso.', 'success');
    }).catch(err => {
      console.error('Error finishing match:', err);
      notify(err instanceof Error ? err.message : 'Não foi possível terminar o jogo. Tente novamente.', 'error');
    });
  }

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
            <Button
              onClick={handleBack}
              type='secondary'
              padding='px-6 py-3'
            >
              Voltar
            </Button>
          </div>
        </div>
    );
  }

  return (
      <div className="flex-1 p-8 max-w-6xl mx-auto">
        <div className="mb-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">{match.tournament.name}</h1>

          <div className='flex gap-4'>
          <Button
            onClick={() => navigate(`/torneios/${match.tournament.id}`)}
            type='secondary'
            padding='px-6 py-3'
          >
            Voltar para Torneio
          </Button>
          <Button
            onClick={handleBack}
            type='secondary'
            padding='px-6 py-3'
          >
            Voltar
          </Button>
          </div>
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

            {isAdminGeneral && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Ações</h3>
                <div className="space-y-3">
                  <>
                    <Button
                      onClick={handleActivateMatch}
                      type='primary'
                      padding='w-full px-4 py-3 flex items-center justify-center'
                      active={match.status == 'scheduled'}
                    >
                      Mudar estado para "Em Curso"
                    </Button>
                    <Button
                      onClick={handleFinishMatch}
                      type='primary'
                      padding='w-full px-4 py-3 flex items-center justify-center'
                      active={match.status == 'in_progress'}
                    >
                      Mudar estado para "Terminado"
                    </Button>
                  </>
                  <Button
                    onClick={handleDownloadSheet}
                    type='info'
                    padding='w-full px-4 py-3 flex items-center justify-center'
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Baixar Ficha de Jogo
                  </Button>

                  <Button
                    onClick={handleDelete}
                    type='danger'
                    padding='w-full px-4 py-3 flex items-center justify-center'
                    confirmation={{
                      title: 'Eliminar jogo',
                      message: 'Tem a certeza que deseja eliminar este jogo? Esta ação não pode ser revertida e todos os dados associados serão permanentemente removidos.',
                      confirmLabel: 'Sim, Eliminar',
                    }}
                    active={isAdminGeneral}
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    Eliminar Jogo
                  </Button>
                </div>
              </div>
            )}

          </div>

          <div className="lg:col-span-2 space-y-6">
            <MatchResultsComponent matchState={[match, setMatch]} />
            <LineupsSection matchState={[match, setMatch]} />
            <CommentsSection match={match} />
          </div>
        </div>
      </div>
  );
};

export default JogoDetails;
