import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { matchesApi, type Match, type MatchUpdate } from '../../api/matches';

const JogoDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [match, setMatch] = useState<Match | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    location: '',
    startTime: '',
    status: 'scheduled' as 'scheduled' | 'in_progress' | 'finished' | 'cancelled',
    homeScore: '',
    awayScore: '',
  });

  // Delete confirmation
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const fetchMatch = async () => {
    if (!id) return;

    try {
      setLoading(true);
      setError('');
      const matchData = await matchesApi.getById(id);
      setMatch(matchData);

      // Initialize form data
      setFormData({
        location: matchData.location,
        startTime: toInputDateTime(matchData.start_time),
        status: matchData.status,
        homeScore: matchData.home_score?.toString() || '',
        awayScore: matchData.away_score?.toString() || '',
      });
    } catch (err) {
      console.error('Error loading match:', err);
      setError(err instanceof Error ? err.message : 'Erro ao carregar dados do jogo');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMatch();
  }, [id]);

  const validateForm = (): boolean => {
    if (!formData.location.trim()) {
      setError('O local é obrigatório');
      return false;
    }

    if (!formData.startTime.trim()) {
      setError('A data e hora são obrigatórias');
      return false;
    }

    if (formData.status === 'finished') {
      if (formData.homeScore === '' || formData.awayScore === '') {
        setError('Os resultados são obrigatórios quando o jogo está terminado');
        return false;
      }

      const homeScore = Number(formData.homeScore);
      const awayScore = Number(formData.awayScore);

      if (isNaN(homeScore) || isNaN(awayScore) || homeScore < 0 || awayScore < 0) {
        setError('Os resultados devem ser números positivos');
        return false;
      }
    }

    return true;
  };

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

  const handleSave = async () => {
    if (!match || !validateForm()) return;

    try {
      setSaving(true);
      setError('');

      const updateData: MatchUpdate = {
        location: formData.location.trim(),
        start_time: new Date(formData.startTime).toISOString(),
        status: formData.status,
      };

      // Include scores for finished matches
      if (formData.status === 'finished') {
        updateData.home_score = Number(formData.homeScore);
        updateData.away_score = Number(formData.awayScore);
      } else {
        // Clear scores if status is not finished
        updateData.home_score = null;
        updateData.away_score = null;
      }

      const updatedMatch = await matchesApi.update(match.id, updateData);
      setMatch(updatedMatch);
      setIsEditing(false);

      // Update form data with the response
      setFormData({
        location: updatedMatch.location,
        startTime: toInputDateTime(updatedMatch.start_time),
        status: updatedMatch.status,
        homeScore: updatedMatch.home_score?.toString() || '',
        awayScore: updatedMatch.away_score?.toString() || '',
      });
    } catch (err) {
      console.error('Error updating match:', err);
      setError(err instanceof Error ? err.message : 'Erro ao atualizar jogo');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!match) return;

    try {
      setError('');
      await matchesApi.delete(match.id);
      navigate(`/geral/torneios/${match.tournament_id}`);
    } catch (err) {
      console.error('Error deleting match:', err);
      setError(err instanceof Error ? err.message : 'Erro ao eliminar jogo');
      setShowDeleteModal(false);
    }
  };

  const handleCancelEdit = () => {
    if (!match) return;

    setFormData({
      location: match.location,
      startTime: toInputDateTime(match.start_time),
      status: match.status,
      homeScore: match.home_score?.toString() || '',
      awayScore: match.away_score?.toString() || '',
    });
    setIsEditing(false);
    setError('');
  };

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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      </div>
    );
  }

  if (!match) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <div className="p-8 max-w-4xl mx-auto">
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
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8 max-w-4xl mx-auto">
        {/* Back Button */}
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

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-md flex items-start">
            <svg className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {/* Main Card */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* Match Header */}
          <div className="bg-gradient-to-r from-teal-500 to-teal-600 text-white p-8">
            <div className="flex justify-between items-center gap-8 mb-4">
              <div className="flex-1 text-right">
                <h2 className="text-2xl font-bold">{match.team_home_name}</h2>
              </div>

              <div className="flex-shrink-0 text-center">
                {match.status === 'finished' && match.home_score !== null && match.away_score !== null ? (
                  <div className="text-5xl font-bold">
                    {match.home_score} - {match.away_score}
                  </div>
                ) : (
                  <div className="text-3xl font-bold opacity-75">VS</div>
                )}
              </div>

              <div className="flex-1">
                <h2 className="text-2xl font-bold">{match.team_away_name}</h2>
              </div>
            </div>

            <div className="text-center">
              {getStatusBadge(match.status)}
            </div>
          </div>

          {/* Match Details / Edit Form */}
          <div className="p-8">
            {!isEditing ? (
              <div className="space-y-6">
                {/* Location */}
                <div className="border-b pb-4">
                  <label className="block text-sm font-medium text-gray-500 mb-1">Local</label>
                  <p className="text-lg text-gray-800">{match.location}</p>
                </div>

                {/* Date and Time */}
                <div className="border-b pb-4">
                  <label className="block text-sm font-medium text-gray-500 mb-1">Data e Hora</label>
                  <p className="text-lg text-gray-800">{formatDateTime(match.start_time)}</p>
                </div>

                {/* Status */}
                <div className="border-b pb-4">
                  <label className="block text-sm font-medium text-gray-500 mb-1">Estado</label>
                  <div>{getStatusBadge(match.status)}</div>
                </div>

                {/* Score Details (if finished) */}
                {match.status === 'finished' && match.home_score !== null && match.away_score !== null && (
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Resultado Final</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <p className="text-sm text-gray-600 mb-1">{match.team_home_name}</p>
                        <p className="text-3xl font-bold text-teal-600">{match.home_score}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-gray-600 mb-1">{match.team_away_name}</p>
                        <p className="text-3xl font-bold text-teal-600">{match.away_score}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-4 pt-4">
                  <button
                    onClick={() => setIsEditing(true)}
                    className="flex-1 px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors flex items-center justify-center"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Editar Jogo
                  </button>
                  <button
                    onClick={() => setShowDeleteModal(true)}
                    className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium transition-colors flex items-center justify-center"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    Eliminar
                  </button>
                </div>
              </div>
            ) : (
              <form onSubmit={(e) => { e.preventDefault(); handleSave(); }} className="space-y-6">
                {/* Teams Display (non-editable) */}
                <div className="bg-gray-50 rounded-lg p-6 text-center">
                  <div className="flex justify-center items-center gap-6 mb-2">
                    <span className="text-lg font-semibold text-gray-800">{match.team_home_name}</span>
                    <span className="text-xl font-bold text-gray-400">VS</span>
                    <span className="text-lg font-semibold text-gray-800">{match.team_away_name}</span>
                  </div>
                  <p className="text-xs text-gray-500">As equipas não podem ser alteradas</p>
                </div>

                {/* Status */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Estado <span className="text-red-500">*</span>
                  </label>
                  <select
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                    value={formData.status}
                    onChange={(e) => setFormData({
                      ...formData,
                      status: e.target.value as 'scheduled' | 'in_progress' | 'finished' | 'cancelled',
                      // Clear scores if status changed from finished to something else
                      homeScore: e.target.value !== 'finished' ? '' : formData.homeScore,
                      awayScore: e.target.value !== 'finished' ? '' : formData.awayScore,
                    })}
                  >
                    <option value="scheduled">Agendado</option>
                    <option value="in_progress">Em Curso</option>
                    <option value="finished">Terminado</option>
                    <option value="cancelled">Cancelado</option>
                  </select>
                </div>

                {/* Scores (only for finished matches) */}
                {formData.status === 'finished' && (
                  <div className="grid grid-cols-2 gap-4 p-4 bg-teal-50 rounded-lg">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        {match.team_home_name} <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="number"
                        min="0"
                        step="1"
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                        value={formData.homeScore}
                        onChange={(e) => setFormData({ ...formData, homeScore: e.target.value })}
                        placeholder="0"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        {match.team_away_name} <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="number"
                        min="0"
                        step="1"
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                        value={formData.awayScore}
                        onChange={(e) => setFormData({ ...formData, awayScore: e.target.value })}
                        placeholder="0"
                        required
                      />
                    </div>
                  </div>
                )}

                {/* Location */}
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

                {/* Date and Time */}
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

                {/* Action Buttons */}
                <div className="flex gap-4 pt-4 border-t">
                  <button
                    type="button"
                    onClick={handleCancelEdit}
                    disabled={saving}
                    className="flex-1 px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={saving}
                    className="flex-1 px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
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
                      'Guardar Alterações'
                    )}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
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
                onClick={() => setShowDeleteModal(false)}
                className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleDelete}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium transition-colors"
              >
                Sim, Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JogoDetails;
