import { useRef, useState } from "react";
import HelpTooltip from "../HelpTooltip";
import { athletesApi } from "../../api/athletes";
import { useNotification } from "../../contexts/NotificationProvider";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";

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

const AthletesMembershipSyncModal = ( {
} : {
}) => {
    const { notify } = useNotification();
    const { popModal } = useModal();

    const [csvFileName, setCsvFileName] = useState<string | null>(null);
    const [parsedPreview, setParsedPreview] = useState<string[]>([]);
    const [csvSubmitting, setCsvSubmitting] = useState(false);
    const csvFileInputRef = useRef<HTMLInputElement>(null);

    const onClose = () => {
        popModal();
        setCsvFileName(null);
        setParsedPreview([]);
        if (csvFileInputRef.current) csvFileInputRef.current.value = "";
    }

    const handleFile = (file: File | null) => {
      setCsvFileName(file?.name ?? null);
      setParsedPreview([]);
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        const text = typeof reader.result === "string" ? reader.result : "";
        setParsedPreview(parseNmecColumnText(text));
      };
      reader.readAsText(file);
    };

    const handleCsvSubmit = async () => {
      setCsvSubmitting(true);
      try {
        const result =
          await athletesApi.syncMembershipFromNmecList(parsedPreview);
        const unmatchedMsg =
          result.unmatched_numbers.length > 0
            ? ` ${result.unmatched_numbers.length} NMEC(s) no ficheiro não correspondem a participantes no âmbito.`
            : "";
        notify(
          `Sincronização concluída: ${result.set_as_socio} sócio(s), ${result.reset_to_non_socio} removido(s).${unmatchedMsg}`,
          result.unmatched_numbers.length > 0 ? "warning" : "success",
        );
        onClose();
      } catch (e) {
        console.error(e);
        notify("Não foi possível aplicar a lista de NMECs.", "error");
      } finally {
        setCsvSubmitting(false);
      }
    };

    return (
        <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
          <h3 className="text-xl font-bold text-gray-800 mb-2">
            Importar NMECs (CSV)
            <HelpTooltip
                text="Sócio: tem quotas em dia e benefícios associados. Podes alterar individualmente ou importar uma lista de NMECs em CSV (primeira coluna)."
                className="ml-1"
            />
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Exporta o Excel como CSV (uma coluna com números mecanográficos).
            Todos os participantes no âmbito passam primeiro a{" "}
            <strong>não sócio</strong>; depois ficam marcados como sócio apenas
            os NMECs desta lista.
          </p>
          <input
            ref={csvFileInputRef}
            type="file"
            accept=".csv,text/csv,text/plain"
            onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
            className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-teal-50 file:text-teal-700"
          />
          {csvFileName && (
            <p
              className="text-xs text-gray-500 mt-2 truncate"
              title={csvFileName}
            >
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
            <Button
                onClick={onClose}
                type="secondary"
                flexible={true}
                disabled={csvSubmitting}
            >
                Cancelar
            </Button>
            <Button
                onClick={handleCsvSubmit}
                type="primary"
                flexible={true}
                disabled={parsedPreview.length === 0 || csvSubmitting}
            >
                {csvSubmitting ? "A aplicar…" : "Aplicar"}
            </Button>
          </div>
        </div>
    );
};

export default AthletesMembershipSyncModal;
