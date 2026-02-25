"use client";

import { FloatingInput } from "@/components/ui/floating-input";
import { FloatingSelect } from "@/components/ui/floating-select";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useOptions } from "@/lib/api/wizard";
import { cn } from "@/lib/utils";
import {
  Settings2,
  Terminal,
  FolderSync,
  Database,
  Server,
  FileCode,
  FileInput,
  FileOutput,
  ArrowRightLeft,
} from "lucide-react";

/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

interface WizardStep4Props {
  data: Record<string, any>;
  onChange: (data: Record<string, any>) => void;
  jobType: string;
}

/* ------------------------------------------------------------------ */
/* Toggle field                                                        */
/* ------------------------------------------------------------------ */

function ToggleField({
  id,
  label,
  description,
  checked,
  onChange,
}: {
  id: string;
  label: string;
  description?: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <div className="flex items-start gap-3">
      <button
        id={id}
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={cn(
          "relative mt-0.5 inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2",
          checked ? "bg-accent" : "bg-border-dark"
        )}
      >
        <span
          className={cn(
            "block h-4 w-4 rounded-full bg-white shadow-sm transition-transform",
            checked ? "translate-x-[18px]" : "translate-x-[2px]"
          )}
        />
      </button>
      <div>
        <label
          htmlFor={id}
          className="text-sm font-medium text-primary cursor-pointer"
        >
          {label}
        </label>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* STANDARD fields                                                     */
/* ------------------------------------------------------------------ */

function StandardFields({
  data,
  update,
}: {
  data: Record<string, any>;
  update: (k: string, v: string) => void;
}) {
  const { data: agents, isLoading } = useOptions("agents");

  const mainScript = (data.main_script as string) ?? "";

  return (
    <div className="space-y-5">
      <FloatingSelect
        id="agent"
        label="Agent"
        value={(data.agent as string) ?? ""}
        onChange={(v) => update("agent", v)}
        options={agents}
        isLoading={isLoading}
        required
        success={!!data.agent}
        icon={<Server className="h-4 w-4" />}
      />

      <FloatingInput
        id="main_script"
        label="Hauptskript"
        value={mainScript}
        onChange={(v) => update("main_script", v)}
        required
        success={mainScript.length > 0}
        icon={<FileCode className="h-4 w-4" />}
        helperText="z.B. /scripts/daily_report.sh"
      />

      <FloatingInput
        id="script_parameters"
        label="Skript-Parameter"
        value={(data.script_parameters as string) ?? ""}
        onChange={(v) => update("script_parameters", v)}
        icon={<Terminal className="h-4 w-4" />}
        helperText="Optionale Kommandozeilen-Parameter"
      />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* FILE_TRANSFER fields                                                */
/* ------------------------------------------------------------------ */

function FileTransferFields({
  data,
  update,
  updateBool,
}: {
  data: Record<string, any>;
  update: (k: string, v: string) => void;
  updateBool: (k: string, v: boolean) => void;
}) {
  const { data: agents, isLoading } = useOptions("agents");

  const transferModes = [
    { label: "Binaer", value: "binary" },
    { label: "Text / ASCII", value: "text" },
  ];

  return (
    <div className="space-y-5">
      <div className="grid gap-5 sm:grid-cols-2">
        <FloatingSelect
          id="source_agent"
          label="Quell-Agent"
          value={(data.source_agent as string) ?? ""}
          onChange={(v) => update("source_agent", v)}
          options={agents}
          isLoading={isLoading}
          required
          success={!!data.source_agent}
          icon={<Server className="h-4 w-4" />}
        />

        <FloatingSelect
          id="target_agent"
          label="Ziel-Agent"
          value={(data.target_agent as string) ?? ""}
          onChange={(v) => update("target_agent", v)}
          options={agents}
          isLoading={isLoading}
          required
          success={!!data.target_agent}
          icon={<Server className="h-4 w-4" />}
        />
      </div>

      <FloatingInput
        id="source_file_pattern"
        label="Quell-Dateimuster"
        value={(data.source_file_pattern as string) ?? ""}
        onChange={(v) => update("source_file_pattern", v)}
        required
        success={!!data.source_file_pattern}
        icon={<FileInput className="h-4 w-4" />}
        helperText="z.B. /data/export/*.csv"
      />

      <FloatingInput
        id="target_file_path"
        label="Ziel-Dateipfad"
        value={(data.target_file_path as string) ?? ""}
        onChange={(v) => update("target_file_path", v)}
        required
        success={!!data.target_file_path}
        icon={<FileOutput className="h-4 w-4" />}
        helperText="z.B. /data/import/"
      />

      <FloatingSelect
        id="transfer_mode"
        label="Uebertragungsmodus"
        value={(data.transfer_mode as string) ?? ""}
        onChange={(v) => update("transfer_mode", v)}
        options={transferModes}
        icon={<ArrowRightLeft className="h-4 w-4" />}
      />

      <ToggleField
        id="overwrite"
        label="Dateien ueberschreiben"
        description="Vorhandene Dateien im Zielverzeichnis ueberschreiben."
        checked={!!data.overwrite}
        onChange={(v) => updateBool("overwrite", v)}
      />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* SAP fields                                                          */
/* ------------------------------------------------------------------ */

function SapFields({
  data,
  update,
}: {
  data: Record<string, any>;
  update: (k: string, v: string) => void;
}) {
  const sapSystems = [
    { label: "PRD - Produktion", value: "PRD" },
    { label: "QAS - Qualitaetssicherung", value: "QAS" },
    { label: "DEV - Entwicklung", value: "DEV" },
  ];

  return (
    <div className="space-y-5">
      <FloatingSelect
        id="sap_system"
        label="SAP-System"
        value={(data.sap_system as string) ?? ""}
        onChange={(v) => update("sap_system", v)}
        options={sapSystems}
        required
        success={!!data.sap_system}
        icon={<Database className="h-4 w-4" />}
      />

      <FloatingInput
        id="sap_client"
        label="Mandant (Client)"
        value={(data.sap_client as string) ?? ""}
        onChange={(v) => update("sap_client", v)}
        required
        success={!!data.sap_client}
        helperText="z.B. 100"
        className="max-w-[200px]"
      />

      <FloatingInput
        id="sap_report"
        label="Report"
        value={(data.sap_report as string) ?? ""}
        onChange={(v) => update("sap_report", v)}
        required
        success={!!data.sap_report}
        icon={<FileCode className="h-4 w-4" />}
        helperText="z.B. ZFINANCE01"
      />

      <FloatingInput
        id="sap_variant"
        label="Variante"
        value={(data.sap_variant as string) ?? ""}
        onChange={(v) => update("sap_variant", v)}
        helperText="Optionale SAP-Report-Variante"
      />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Main Component                                                      */
/* ------------------------------------------------------------------ */

export default function WizardStep4({
  data,
  onChange,
  jobType,
}: WizardStep4Props) {
  function update(key: string, value: string) {
    onChange({ ...data, [key]: value });
  }

  function updateBool(key: string, value: boolean) {
    onChange({ ...data, [key]: value });
  }

  const jobTypeLabel: Record<string, string> = {
    STANDARD: "Standard",
    FILE_TRANSFER: "Dateitransfer",
    SAP: "SAP",
  };

  const jobTypeIcon: Record<string, React.ElementType> = {
    STANDARD: Terminal,
    FILE_TRANSFER: FolderSync,
    SAP: Database,
  };

  const Icon = jobTypeIcon[jobType] ?? Settings2;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Icon className="h-5 w-5 text-accent" />
            Job-spezifische Parameter
          </CardTitle>
          <Badge>{jobTypeLabel[jobType] ?? jobType}</Badge>
        </div>
        <CardDescription>
          Konfigurieren Sie die Parameter fuer den ausgewaehlten Job-Typ.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {jobType === "STANDARD" && (
          <StandardFields data={data} update={update} />
        )}
        {jobType === "FILE_TRANSFER" && (
          <FileTransferFields
            data={data}
            update={update}
            updateBool={updateBool}
          />
        )}
        {jobType === "SAP" && <SapFields data={data} update={update} />}
        {!["STANDARD", "FILE_TRANSFER", "SAP"].includes(jobType) && (
          <p className="text-sm text-muted-foreground py-4">
            Bitte waehlen Sie zuerst einen Job-Typ in Schritt 3 aus.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
