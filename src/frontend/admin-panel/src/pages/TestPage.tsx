import { useEffect, useState } from "react";
import { type TournamentDetail, tournamentsApi } from "../api/tournaments";
import { type AdminDetail, administratorsApi } from "../api/admins";
import AdminEditModal from "../components/admins/AdminEditModal";
import { btn } from "../styles/buttonStyles";
import Button from "../components/utils/Button";

const TestPage = () => {

    const renderButton = (style: string) => {
        return (
            <button className={`flex-1 px-4 py-2 rounded-md ${style}`}>
                Button
            </button>
        );
    }

    return (
        <div className="p-4 bg-black text-white min-h-screen">
            <h1 className="text-2xl font-bold mb-4">Página de Teste</h1>
            <div className="flex gap-4 mt-6">
                {renderButton(btn.primary)}
                {renderButton(btn.danger)}
                {/* {renderButton(btn.dangerLight)} */}
                {/* {renderButton(btn.dangerGhost)} */}
                {renderButton(btn.secondary)}
                {/* {renderButton(btn.secondaryAlt)} */}
                {/* {renderButton(btn.info)} */}
                {renderButton(btn.infoStrong)}
                {renderButton(btn.success)}
            </div>
            <div className="flex gap-4 mt-6">
                <Button
                    onClick={() => alert("Button clicked!")}
                    label="Primary Button"
                    type="primary"
                    confirmation={{
                        title: "Confirm Action",
                        message: "Are you sure you want to perform this action?",
                        confirmLabel: "Yes, do it!",
                        cancelLabel: "No, cancel"
                    }}
                />

                <Button
                    onClick={() => alert("Danger Button clicked!")}
                    label="Danger Button"
                    type="danger"
                    confirmation={{
                        title: "Confirm Deletion",
                        message: "Are you sure you want to delete this item? This action cannot be undone.",
                        confirmLabel: "Yes, delete it!",
                        cancelLabel: "No, keep it"
                    }}
                />
            </div>
        </div>
    )
}

export default TestPage
