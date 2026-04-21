import { useEffect, useState } from "react";
import { type AthleteListItem, athletesApi } from "../api/athletes";
import { type StaffListItem, staffApi } from "../api/staff";
import AthletesListComponent from "../components/athletes/AthletesListComponent";
import StaffListComponent from "../components/staff/StaffListComponent";
import { useNotification } from "../contexts/NotificationProvider";

const TestPage = () => {
    const { notify } = useNotification();

    const [athletes, setAthletes] = useState<AthleteListItem[] | null>(null);
    const [staff, setStaff] = useState<StaffListItem[] | null>(null);

    const [activeTab, setActiveTab] = useState<'athletes' | 'staff'>('athletes');
    const [searchQuery, setSearchQuery] = useState("");

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
            member.staff_number!.toString().includes(query) ||
            member.contact!.toLowerCase().includes(query));
    }) : null;

    return (
      <div className="space-y-6">
        <div className="flex-1">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Pesquisar por nome, NMEC ou curso..."
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
          />
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
              <AthletesListComponent athletes={filteredAthletes} />
            )}
            {activeTab === "staff" && (
              <StaffListComponent staffList={filteredStaff} />
            )}
          </div>
        </div>
      </div>
    );
}

export default TestPage
