"use client";

import { useState, useEffect } from "react";
import { FormField, InputField, TextAreaField, SelectField } from "../../components/ui/FormField";
import { Combobox } from "../../components/ui/Combobox";
import { useOptions } from "../../hooks/useOptions";

interface WizardSession {
    session_id: string;
    params: Record<string, string | boolean | number>;
    detected_job_type: string | null;
    ai_suggestions: Record<string, string>;
}

interface Props {
    session: WizardSession | null;
    onSave: (stepId: string, data: Record<string, unknown>, shouldAdvance?: boolean) => Promise<void>;
    isLoading: boolean;
}

export default function WizardStep4JobDetails({ session, onSave, isLoading }: Props) {
    const jobType = session?.detected_job_type || (session?.params.job_type as string) || "STANDARD";
    const { options: agentOptions } = useOptions("agent");

    // Initialize with saved params OR AI suggestions (params take precedence)
    const s = session?.ai_suggestions;

    // Standard Job fields
    const [agentDetail, setAgentDetail] = useState(session?.params.agent_detail as string || s?.agent_detail || "");
    const [mainScript, setMainScript] = useState(session?.params.main_script as string || "");
    const [scriptType, setScriptType] = useState(session?.params.script_type as string || "Windows");

    // File Transfer fields
    const [sourceAgent, setSourceAgent] = useState(session?.params.source_agent as string || s?.source_agent || "");
    const [targetAgent, setTargetAgent] = useState(session?.params.target_agent as string || s?.target_agent || "");
    const [sourceFile, setSourceFile] = useState(session?.params.source_file_pattern as string || s?.source_file_pattern || "");
    const [targetPath, setTargetPath] = useState(session?.params.target_file_path as string || s?.target_file_path || "");
    const [sourceLogin, setSourceLogin] = useState(session?.params.source_login_object as string || "");
    const [targetLogin, setTargetLogin] = useState(session?.params.target_login_object as string || "");

    // SAP fields
    const [sapSystem, setSapSystem] = useState(session?.params.sap_system as string || s?.sap_system || "");
    const [sapClient, setSapClient] = useState(session?.params.sap_client as string || "");
    const [sapReport, setSapReport] = useState(session?.params.sap_report as string || s?.sap_report || "");
    const [sapVariant, setSapVariant] = useState(session?.params.sap_variant as string || "");

    // NOTE: Removed useEffect that synced ai_suggestions -> state to prevent overwriting user edits on navigation.

    // Auto-save effect
    useEffect(() => {
        const timer = setTimeout(() => {
            let data: Record<string, unknown> = {};
            let hasChanges = false;

            if (jobType === "STANDARD") {
                hasChanges =
                    agentDetail !== session?.params.agent_detail ||
                    mainScript !== session?.params.main_script ||
                    scriptType !== session?.params.script_type;
                if (hasChanges) {
                    data = { agent_detail: agentDetail, main_script: mainScript, script_type: scriptType };
                }
            } else if (jobType === "FILE_TRANSFER") {
                hasChanges =
                    sourceAgent !== session?.params.source_agent ||
                    targetAgent !== session?.params.target_agent ||
                    sourceFile !== session?.params.source_file_pattern ||
                    targetPath !== session?.params.target_file_path;
                if (hasChanges) {
                    data = {
                        source_agent: sourceAgent,
                        target_agent: targetAgent,
                        source_file_pattern: sourceFile,
                        target_file_path: targetPath,
                        source_login_object: sourceLogin,
                        target_login_object: targetLogin,
                    };
                }
            } else if (jobType === "SAP") {
                hasChanges =
                    sapSystem !== session?.params.sap_system ||
                    sapReport !== session?.params.sap_report;
                if (hasChanges) {
                    data = {
                        sap_system: sapSystem,
                        sap_client: sapClient,
                        sap_report: sapReport,
                        sap_variant: sapVariant,
                    };
                }
            }

            if (Object.keys(data).length > 0) {
                onSave("job_details", data, false);
            }
        }, 1000);

        return () => clearTimeout(timer);
    }, [agentDetail, mainScript, scriptType, sourceAgent, targetAgent, sourceFile, targetPath, sourceLogin, targetLogin, sapSystem, sapClient, sapReport, sapVariant, jobType, onSave, session?.params]);

    const handleContinue = async () => {
        let data: Record<string, unknown> = {};

        if (jobType === "STANDARD") {
            data = { agent_detail: agentDetail, main_script: mainScript, script_type: scriptType };
        } else if (jobType === "FILE_TRANSFER") {
            data = {
                source_agent: sourceAgent, target_agent: targetAgent,
                source_file_pattern: sourceFile, target_file_path: targetPath,
                source_login_object: sourceLogin || null, target_login_object: targetLogin || null,
            };
        } else if (jobType === "SAP") {
            data = {
                sap_system: sapSystem, sap_client: sapClient,
                sap_report: sapReport, sap_variant: sapVariant || null,
            };
        }

        await onSave("job_details", data);
    };

    const isValid = () => {
        if (jobType === "STANDARD") return agentDetail.trim() && mainScript.trim();
        if (jobType === "FILE_TRANSFER") return sourceAgent.trim() && targetAgent.trim() && sourceFile.trim();
        if (jobType === "SAP") return sapSystem.trim() && sapReport.trim();
        return false;
    };

    const descriptions: Record<string, string> = {
        STANDARD: "Konfigurieren Sie Ihr Script und den Ausführungsserver.",
        FILE_TRANSFER: "Definieren Sie Quell- und Zielserver für den Dateitransfer.",
        SAP: "Geben Sie die SAP-System-Details ein.",
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-xl font-bold text-gray-900 mb-1">
                    Schritt 4: Job-Details
                </h2>
                <p className="text-gray-500 text-sm">{descriptions[jobType]}</p>
            </div>

            {/* STANDARD Job Form */}
            {jobType === "STANDARD" && (
                <div className="space-y-5">
                    <FormField
                        label="Agent / Server"
                        hint="Der Automation Engine Agent, auf dem das Script ausgeführt werden soll. Dies ist typischerweise der Hostname oder eine Agent-Gruppe."
                        required
                    >
                        <Combobox
                            value={agentDetail}
                            onChange={setAgentDetail}
                            options={agentOptions}
                            placeholder="Agent auswählen oder eingeben..."
                        />
                    </FormField>

                    <FormField
                        label="Script-Typ"
                        hint="Der Interpreter für Ihr Script. Windows CMD für Batch-Dateien, PowerShell für PS1-Scripts, Unix Shell für Bash, oder Python."
                    >
                        <SelectField
                            value={scriptType}
                            onChange={(e) => setScriptType(e.target.value)}
                            options={[
                                { value: "Windows", label: "Windows (CMD/Batch)" },
                                { value: "PowerShell", label: "PowerShell" },
                                { value: "Unix", label: "Unix Shell" },
                                { value: "Python", label: "Python" },
                            ]}
                        />
                    </FormField>

                    <FormField
                        label="Script / Befehl"
                        hint="Der auszuführende Befehl oder Script-Code. Kann ein einzelner Befehl oder ein mehrzeiliges Script sein."
                        required
                    >
                        <TextAreaField
                            value={mainScript}
                            onChange={(e) => setMainScript(e.target.value)}
                            placeholder="echo Hallo Welt"
                            rows={5}
                            className="font-mono text-sm"
                        />
                    </FormField>
                </div>
            )}

            {/* FILE_TRANSFER Form */}
            {jobType === "FILE_TRANSFER" && (
                <div className="space-y-5">
                    <div className="grid grid-cols-2 gap-4">
                        <FormField
                            label="Quell-Agent"
                            hint="Der Agent auf dem System, von dem die Datei(en) kopiert werden sollen."
                            required
                        >
                            <Combobox
                                value={sourceAgent}
                                onChange={setSourceAgent}
                                options={agentOptions}
                                placeholder="Agent auswählen..."
                            />
                        </FormField>

                        <FormField
                            label="Ziel-Agent"
                            hint="Der Agent auf dem Zielsystem, wohin die Datei(en) kopiert werden sollen."
                            required
                        >
                            <Combobox
                                value={targetAgent}
                                onChange={setTargetAgent}
                                options={agentOptions}
                                placeholder="Agent auswählen..."
                            />
                        </FormField>
                    </div>

                    <FormField
                        label="Quell-Dateipfad"
                        hint="Der vollständige Pfad zur Quelldatei oder ein Muster mit Wildcards (z.B. /data/*.csv oder E:\\Backup\\*.txt)."
                        required
                    >
                        <InputField
                            value={sourceFile}
                            onChange={(e) => setSourceFile(e.target.value)}
                            placeholder="z.B. /data/export/*.csv"
                        />
                    </FormField>

                    <FormField
                        label="Ziel-Verzeichnis"
                        hint="Das Zielverzeichnis auf dem Zielsystem. Dateien werden hierhin kopiert."
                    >
                        <InputField
                            value={targetPath}
                            onChange={(e) => setTargetPath(e.target.value)}
                            placeholder="z.B. /backup/"
                        />
                    </FormField>

                    <div className="grid grid-cols-2 gap-4">
                        <FormField
                            label="Quell-Login-Objekt"
                            hint="Optional: Ein Login-Objekt für die Authentifizierung am Quellsystem (z.B. für SFTP)."
                        >
                            <InputField
                                value={sourceLogin}
                                onChange={(e) => setSourceLogin(e.target.value)}
                                placeholder="Optional"
                            />
                        </FormField>

                        <FormField
                            label="Ziel-Login-Objekt"
                            hint="Optional: Ein Login-Objekt für die Authentifizierung am Zielsystem."
                        >
                            <InputField
                                value={targetLogin}
                                onChange={(e) => setTargetLogin(e.target.value)}
                                placeholder="Optional"
                            />
                        </FormField>
                    </div>
                </div>
            )}

            {/* SAP Form */}
            {jobType === "SAP" && (
                <div className="space-y-5">
                    <div className="grid grid-cols-2 gap-4">
                        <FormField
                            label="SAP System"
                            hint="Die System-ID (SID) des SAP-Systems, z.B. P01 für Produktion oder D01 für Entwicklung."
                            required
                        >
                            <InputField
                                value={sapSystem}
                                onChange={(e) => setSapSystem(e.target.value)}
                                placeholder="z.B. P01, D01"
                            />
                        </FormField>

                        <FormField
                            label="Mandant"
                            hint="Die SAP-Mandantennummer (Client), typischerweise 100, 200 oder 800."
                        >
                            <InputField
                                value={sapClient}
                                onChange={(e) => setSapClient(e.target.value)}
                                placeholder="z.B. 100"
                            />
                        </FormField>
                    </div>

                    <FormField
                        label="Report / Programm"
                        hint="Der technische Name des SAP-Reports oder ABAP-Programms, das ausgeführt werden soll."
                        required
                    >
                        <InputField
                            value={sapReport}
                            onChange={(e) => setSapReport(e.target.value)}
                            placeholder="z.B. ZREPORT_DAILY"
                        />
                    </FormField>

                    <FormField
                        label="Variante"
                        hint="Optional: Eine gespeicherte Variante für den Report mit vordefinierten Selektionsparametern."
                    >
                        <InputField
                            value={sapVariant}
                            onChange={(e) => setSapVariant(e.target.value)}
                            placeholder="Optional"
                        />
                    </FormField>
                </div>
            )}
        </div>
    );
}
