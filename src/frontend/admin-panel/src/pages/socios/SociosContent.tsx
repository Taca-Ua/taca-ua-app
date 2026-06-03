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
import TabSystem from '../../components/TabSystem';

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

const AthletesTab = ( {
  athletesState
} : {
  athletesState: [AthleteListItem[] | null, React.Dispatch<React.SetStateAction<AthleteListItem[] | null>>]
} ) => {

  const [athletes, setAthletes] = athletesState;
  const { notify } = useNotification();

  useEffect(() => {
    if (athletes) return; // Don't fetch if we already have data
    athletesApi
      .getAll()
      .then((data) => {
        setAthletes(data);
      })
      .catch((err) => {
        console.error("Failed to fetch athletes:", err);
        notify("Erro ao carregar atletas. Tente novamente.", "error");
        setAthletes([]);
      });
  }, [athletesState]);

  return <AthletesListComponent athletesState={athletesState} />;
};

const StaffTab = ( {
  staffListState
} : {
  staffListState: [StaffListItem[] | null, React.Dispatch<React.SetStateAction<StaffListItem[] | null>>]
} ) => {
  const [staff, setStaff] = staffListState;
  const { notify } = useNotification();

  useEffect(() => {
    if (staff) return; // Don't fetch if we already have data
    staffApi
      .getAll()
      .then((data) => {
        setStaff(data);
      })
      .catch((err) => {
        console.error("Failed to fetch staff:", err);
        notify("Erro ao carregar staff. Tente novamente.", "error");
        setStaff([]);
      });
  }, [staffListState]);

  return <StaffListComponent staffListState={[staff, setStaff]} />;
};

export default function SociosContent() {
  const { pushModal } = useModal();
  const { isAdminGeneral } = useAuth();

  const [searchQuery, setSearchQuery] = useState('');

  const [activeTab, setActiveTab] = useState<'athletes' | 'staff'>('athletes');

  const [athletes, setAthletes] = useState<AthleteListItem[] | null>(null);
  const [staff, setStaff] = useState<StaffListItem[] | null>(null);


  const filteredAthletes = athletes ? athletes.filter((athlete) => {
    const query = searchQuery.toLowerCase();
    return (athlete.name.toLowerCase().includes(query) ||
        athlete.student_number.toString().includes(query) ||
        athlete.course?.name.toLowerCase().includes(query));
  }) : null;

  const filteredStaff = staff ? staff.filter((member) => {
    const query = searchQuery.toLowerCase();
    return (member.name.toLowerCase().includes(query) ||
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

        <TabSystem
          elements={[
            {id: "athletes", label: "Atletas", content: <AthletesTab athletesState={[filteredAthletes, setAthletes]} />},
            {id: "staff", label: "Staff", content: <StaffTab staffListState={[filteredStaff, setStaff]} />}
          ]}
          onTabChange={(tabId) => {
            setActiveTab(tabId as 'athletes' | 'staff');
          }}
        />
      </div>
    </div>
  );
}
