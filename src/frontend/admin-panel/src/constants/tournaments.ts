// Status order for sorting tournaments
export const TOURNAMENT_STATUS_ORDER: Record<string, number> = {
  active: 0,
  draft: 1,
  finished: 2,
};

// Status labels in Portuguese
export const TOURNAMENT_STATUS_LABELS: Record<string, string> = {
  active: 'Ativo',
  draft: 'Rascunho',
  finished: 'Finalizado',
};

// Status colors for display
export const TOURNAMENT_STATUS_COLORS: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  draft: 'bg-yellow-100 text-yellow-800',
  finished: 'bg-gray-100 text-gray-600',
};
