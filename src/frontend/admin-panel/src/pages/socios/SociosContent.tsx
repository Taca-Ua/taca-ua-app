import { useState, useEffect } from 'react';
import { useNotification } from '../../contexts/NotificationProvider';
import Button from '../../components/utils/Button';
import AthletesListComponent from '../../components/athletes/AthletesListComponent';
import StaffListComponent from '../../components/staff/StaffListComponent';
import AthleteCreateModal from '../../components/athletes/AthleteCreateModal';
import StaffCreateModal from '../../components/staff/StaffCreateModal';
import { staffApi, type StaffListItem } from '../../api/staff';
import { athletesApi, type AthleteListItem } from '../../api/athletes';
import AthletesMembershipSyncModal from '../../components/athletes/AthletesMembershipSyncModal';
import { useModal } from '../../contexts/ModalContext';
import { useAuth } from '../../hooks/useAuth';

export type SociosVariant = 'geral' | 'nucleo';

/** Ficheiro CSV (ou Excel guardado como CSV): primeira coluna = NMEC por linha. */
export function parseNmecColumnText(text: string): string[] {
  // Strip UTF-8 BOM if present (common in Excel-exported CSVs)
  const stripped = text.replace(/^\uFEFF/, '');
  const lines = stripped.split(/\r?\n/);
  const out: string[] = [];
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    const firstCell = trimmed.split(/[,;\t]/)[0]?.trim() ?? '';
    const unquoted = firstCell.replace(/^["']|["']$/g, '').trim();
    if (unquoted) out.push(unquoted);
  }
  return out;
}

export default function SociosContent() {
  const { notify } = useNotification();
  const { pushModal } = useModal();
  const { isAdminGeneral } = useAuth();

  const [searchQuery, setSearchQuery] = useState('');

  const [activeTab, setActiveTab] = useState<'athletes' | 'staff'>('athletes');

  const [athletes, setAthletes] = useState<AthleteListItem[] | null>(null);
  const [staff, setStaff] = useState<StaffListItem[] | null>(null);

  useEffect(() => {
      if (activeTab !== 'athletes') return;
      if (athletes !== null) return; // Don't refetch if we already have data
      athletesApi.getAll().then((data) => {
          setAthletes(data);
      }).catch((err) => {
          console.error("Failed to fetch athletes:", err);
          notify("Erro ao carregar atletas. Tente novamente.", "error");
      });
  }, [activeTab]);

  useEffect(() => {
      if (activeTab !== 'staff') return;
      if (staff !== null) return; // Don't refetch if we already have data
      staffApi.getAll().then((data) => {
          setStaff(data);
      }).catch((err) => {
          console.error("Failed to fetch staff:", err);
          notify("Erro ao carregar staff. Tente novamente.", "error");
      });
  }, [activeTab]);

  const filteredAthletes = athletes ? athletes.filter((athlete) => {
    const query = searchQuery.toLowerCase();
    return (athlete.full_name.toLowerCase().includes(query) ||
        athlete.student_number.toString().includes(query) ||
        athlete.course?.name.toLowerCase().includes(query));
  }) : null;

  const filteredStaff = staff ? staff.filter((member) => {
    const query = searchQuery.toLowerCase();
    return (member.full_name.toLowerCase().includes(query) ||
        member.staff_number?.toString().includes(query) ||
        member.contact?.toLowerCase().includes(query));
  }) : null;

  return (
    <div className="flex-1 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Membros</h1>
            <p className="text-gray-600 text-sm mt-1">
              Participantes da TACA-UA
            </p>
          </div>
          <div className="flex gap-3">
            <Button
              onClick={() => pushModal(<AthletesMembershipSyncModal />)}
              type="info"
              active={activeTab === "athletes" && isAdminGeneral}
            >
              Importar lista (CSV)
            </Button>
            <Button
              onClick={() => {
                switch (activeTab) {
                  case "athletes":
                    pushModal(<AthleteCreateModal
                      onCreate={(newAthlete) => {
                        setAthletes((prev) =>
                          prev ? [newAthlete, ...prev] : [newAthlete],
                        );
                      }}
                    />);
                    break;
                  case "staff":
                    pushModal(
                      <StaffCreateModal
                        onCreate={(newMember) => {
                          setStaff((prev) => (prev ? [newMember, ...prev] : [newMember]));
                        }}
                      />
                    );
                    break;
                }
              }}
              flexible={true}
            >
              + Adicionar {activeTab === "athletes" ? "Atleta" : "Staff"}
            </Button>
          </div>
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
        </div>

        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="border-b border-gray-200">
            <div className="flex">
              <button
                onClick={() => setActiveTab("athletes")}
                className={`px-6 py-4 font-bold text-2xl transition-colors border-b-2 ${
                  activeTab === "athletes"
                    ? "border-teal-500 text-teal-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                Atletas
              </button>
              <button
                onClick={() => setActiveTab("staff")}
                className={`px-6 py-4 font-bold text-2xl transition-colors border-b-2 ${
                  activeTab === "staff"
                    ? "border-teal-500 text-teal-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                Staff
              </button>
            </div>
          </div>
          <div className="w-full p-4 border-b">
            {activeTab === "athletes" && (
              <AthletesListComponent athletesState={[filteredAthletes, setAthletes]} />
            )}
            {activeTab === "staff" && (
              <StaffListComponent staffListState={[filteredStaff, setStaff]} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
