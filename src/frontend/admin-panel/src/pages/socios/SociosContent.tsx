import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import HelpTooltip from '../../components/HelpTooltip';
import { studentsApi, type Student } from '../../api/members';
import { useNotification } from '../../contexts/NotificationProvider';
import { btn } from '../../styles/buttonStyles';

export type SociosVariant = 'geral' | 'nucleo';

/** Ficheiro CSV (ou Excel guardado como CSV): primeira coluna = NMEC por linha. */
export function parseNmecColumnText(text: string): string[] {
  const lines = text.split(/\r?\n/);
  const out: string[] = [];
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    const firstCell = trimmed.split(/[,;\t]/)[0]?.trim() ?? '';
    const unquoted = firstCell.replace(/^["']|["']$/g, '');
    if (unquoted) out.push(unquoted);
  }
  return out;
}

function SocioToggle({
  checked,
  disabled,
  onToggle,
}: {
  checked: boolean;
  disabled: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={(e) => {
        e.preventDefault();
        e.stopPropagation();
        onToggle();
      }}
      className={`
        relative inline-flex h-8 w-14 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors
        focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${checked ? 'bg-teal-600' : 'bg-gray-200'}
      `}
    >
      <span
        className={`
          pointer-events-none inline-block h-7 w-7 transform rounded-full bg-white shadow ring-0 transition
          ${checked ? 'translate-x-6' : 'translate-x-0.5'}
        `}
      />
    </button>
  );
}

interface SociosContentProps {
  variant: SociosVariant;
}

export default function SociosContent({ variant }: SociosContentProps) {
  const { notify } = useNotification();
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [socioFilter, setSocioFilter] = useState<'all' | 'socio' | 'nao_socio'>('all');
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [csvModalOpen, setCsvModalOpen] = useState(false);
  const [csvFileName, setCsvFileName] = useState<string | null>(null);
  const [parsedPreview, setParsedPreview] = useState<string[]>([]);
  const [csvSubmitting, setCsvSubmitting] = useState(false);

  const loadStudents = useCallback(async () => {
    try {
      setLoading(true);
      const data = await studentsApi.getAll();
      setStudents(data);
    } catch (err) {
      console.error(err);
      notify('Não foi possível carregar os participantes.', 'error');
    } finally {
      setLoading(false);
    }
  }, [notify]);

  useEffect(() => {
    loadStudents();
  }, [loadStudents]);

  const q = searchQuery.trim().toLowerCase();
  const filtered = students
    .filter((s) => {
      if (socioFilter === 'socio' && !s.is_member) return false;
      if (socioFilter === 'nao_socio' && s.is_member) return false;
      if (!q) return true;
      const name = s.full_name.toLowerCase();
      const nmec = s.student_number.toLowerCase();
      const course = s.course?.name?.toLowerCase() ?? '';
      return name.includes(q) || nmec.includes(q) || course.includes(q);
    })
    .sort((a, b) => a.full_name.localeCompare(b.full_name));

  const handleToggleSocio = async (student: Student) => {
    const next = !student.is_member;
    setPendingId(student.id);
    try {
      const updated = await studentsApi.update(student.id, { is_member: next });
      setStudents((prev) =>
        prev.map((s) => (s.id === student.id ? { ...s, is_member: updated.is_member } : s)),
      );
      notify(next ? 'Marcado como sócio.' : 'Removido o estado de sócio.', 'success');
    } catch (e) {
      console.error(e);
      notify('Não foi possível atualizar o estado de sócio.', 'error');
    } finally {
      setPendingId(null);
    }
  };

  const handleFile = (file: File | null) => {
    setCsvFileName(file?.name ?? null);
    setParsedPreview([]);
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const text = typeof reader.result === 'string' ? reader.result : '';
      setParsedPreview(parseNmecColumnText(text));
    };
    reader.readAsText(file);
  };

  const handleCsvSubmit = async () => {
    setCsvSubmitting(true);
    try {
      const result = await studentsApi.syncMembershipFromNmecList(parsedPreview);
      await loadStudents();
      const unmatchedMsg =
        result.unmatched_numbers.length > 0
          ? ` ${result.unmatched_numbers.length} NMEC(s) no ficheiro não correspondem a participantes no âmbito.`
          : '';
      notify(
        `Sincronização concluída: ${result.set_as_socio} sócio(s), ${result.reset_to_non_socio} removido(s).${unmatchedMsg}`,
        result.unmatched_numbers.length > 0 ? 'warning' : 'success',
      );
      setCsvModalOpen(false);
      setCsvFileName(null);
      setParsedPreview([]);
    } catch (e) {
      console.error(e);
      notify('Não foi possível aplicar a lista de NMECs.', 'error');
    } finally {
      setCsvSubmitting(false);
    }
  };

  return (
    <div className="flex-1 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Sócios</h1>
            <p className="text-gray-600 text-sm mt-1">
              Participantes (estudantes) e estado de sócio do núcleo
              {variant === 'geral' ? ' (todos os núcleos)' : ''}.
              <HelpTooltip
                text="Sócio: tem quotas em dia e benefícios associados. Podes alterar individualmente ou importar uma lista de NMECs em CSV (primeira coluna)."
                className="ml-1"
              />
            </p>
          </div>
          <button
            type="button"
            onClick={() => setCsvModalOpen(true)}
            className={`${btn.primary} px-4 py-2 rounded-md font-medium whitespace-nowrap`}
          >
            Importar lista (CSV)
          </button>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Pesquisar por nome, NMEC ou curso..."
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div className="sm:w-56">
            <select
              value={socioFilter}
              onChange={(e) => setSocioFilter(e.target.value as typeof socioFilter)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="all">Todos</option>
              <option value="socio">Sócios</option>
              <option value="nao_socio">Não sócios</option>
            </select>
          </div>
        </div>

        {loading && (
          <div className="flex justify-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500" />
          </div>
        )}

        {!loading && (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-800">
                Participantes
                <span className="text-gray-500 font-normal ml-2">({filtered.length})</span>
              </h2>
            </div>
            {filtered.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                Nenhum participante corresponde aos filtros.
              </div>
            ) : (
              <ul className="divide-y divide-gray-100 max-h-[640px] overflow-y-auto">
                {filtered.map((s) => (
                  <li
                    key={s.id}
                    className="px-6 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 hover:bg-gray-50"
                  >
                    <div className="min-w-0 flex-1">
                      {variant === 'nucleo' ? (
                        <Link
                          to={`/nucleo/membros/participant/${s.id}`}
                          className="font-medium text-teal-700 hover:underline truncate block"
                        >
                          {s.full_name}
                        </Link>
                      ) : (
                        <span className="font-medium text-gray-800 truncate block">{s.full_name}</span>
                      )}
                      <div className="text-sm text-gray-600 mt-0.5">
                        NMEC {s.student_number}
                        {s.course?.name ? ` · ${s.course.name}` : ''}
                      </div>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <span className="text-sm text-gray-600 w-24 text-right sm:text-left">
                        {s.is_member ? 'Sócio' : 'Não sócio'}
                      </span>
                      <SocioToggle
                        checked={s.is_member}
                        disabled={pendingId === s.id}
                        onToggle={() => handleToggleSocio(s)}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>

      {csvModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-lg w-full p-6 shadow-xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold text-gray-800 mb-2">Importar NMECs (CSV)</h3>
            <p className="text-sm text-gray-600 mb-4">
              Exporta o Excel como CSV (uma coluna com números mecanográficos). Todos os participantes no
              âmbito passam primeiro a <strong>não sócio</strong>; depois ficam marcados como sócio apenas os
              NMECs desta lista.
            </p>
            <input
              type="file"
              accept=".csv,text/csv,text/plain"
              onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
              className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-teal-50 file:text-teal-700"
            />
            {csvFileName && (
              <p className="text-xs text-gray-500 mt-2 truncate" title={csvFileName}>
                {csvFileName}
              </p>
            )}
            {parsedPreview.length > 0 && (
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-700">
                  Pré-visualização: {parsedPreview.length} NMEC(s) (primeiros 15)
                </p>
                <ul className="mt-2 text-xs font-mono bg-gray-50 rounded p-2 max-h-32 overflow-y-auto border border-gray-100">
                  {parsedPreview.slice(0, 15).map((n) => (
                    <li key={n}>{n}</li>
                  ))}
                </ul>
              </div>
            )}
            <div className="flex gap-3 mt-6">
              <button
                type="button"
                onClick={() => {
                  setCsvModalOpen(false);
                  setCsvFileName(null);
                  setParsedPreview([]);
                }}
                className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md font-medium`}
                disabled={csvSubmitting}
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleCsvSubmit}
                disabled={parsedPreview.length === 0 || csvSubmitting}
                className={`flex-1 px-4 py-2 ${btn.primary} rounded-md font-medium disabled:opacity-50`}
              >
                {csvSubmitting ? 'A aplicar…' : 'Aplicar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
