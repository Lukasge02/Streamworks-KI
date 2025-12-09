"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { Editor } from "@monaco-editor/react";
import { ArrowLeft, Download, Save, Sparkles, Send, RefreshCw, Code, Settings, FileCode, CheckCircle2, AlertCircle, Eye, EyeOff, MessageSquare } from "lucide-react";
import AppLayout from "../../components/AppLayout";
import { Button } from "../../components/ui/button";
import { cn } from "../../utils/cn";
import ReactMarkdown from 'react-markdown';

// --- Types ---

interface SessionData {
    id: string;
    name: string;
    status: string;
    params: Record<string, string | number | boolean>;
    job_type: string;
}

interface ParameterConfig {
    key: string;
    label: string;
    type: "text" | "select" | "textarea" | "time" | "boolean" | "number";
    options?: string[];
    category: "stream" | "job" | "schedule" | "contact" | "advanced" | "system" | "dependency";
    helperText?: string;
}

// --- Master Parameter Configuration ---

const ALL_STREAM_PARAMS: ParameterConfig[] = [
    { key: "stream_name", label: "Stream-Name", type: "text", category: "stream" },
    { key: "short_description", label: "Kurzbeschreibung", type: "text", category: "stream" },
    { key: "stream_documentation", label: "Dokumentation", type: "textarea", category: "stream" },
    { key: "stream_owner", label: "Verantwortlicher", type: "text", category: "stream" },
    { key: "stream_priority", label: "Priorität (0-10)", type: "number", category: "stream" },
    { key: "stream_queue", label: "Queue", type: "text", category: "stream" },
    { key: "max_stream_runs", label: "Max. parallele Läufe", type: "number", category: "stream" },
    { key: "status_flag", label: "Aktiv", type: "boolean", category: "stream" },
];

const STREAM_ADVANCED_PARAMS: ParameterConfig[] = [
    { key: "business_service_flag", label: "Business Service", type: "boolean", category: "advanced" },
    { key: "enable_stream_run_cancelation", label: "Abbruch erlaubt", type: "boolean", category: "advanced" },
    { key: "concurrent_stream_runs_enabled", label: "Parallel-Lauf erlaubt", type: "boolean", category: "advanced" },
    { key: "deploy_as_active", label: "Aktiv deployen", type: "boolean", category: "advanced" },
    { key: "tags", label: "Tags", type: "text", category: "advanced", helperText: "Kommagetrennt" },
    { key: "run_variables", label: "Variablen", type: "textarea", category: "advanced" },
    { key: "automatic_prepared_runs", label: "Auto. Prepared Runs", type: "number", category: "advanced" },
    { key: "auto_preparation_type", label: "Auto. Prep. Type", type: "select", options: ["Complete", "Partial"], category: "advanced" },
];

const SYSTEM_PARAMS: ParameterConfig[] = [
    { key: "stream_path", label: "Stream Pfad", type: "text", category: "system", helperText: "z.B. /Abteilung/Team" },
    { key: "master_stream_id", label: "Master Stream ID", type: "text", category: "system" },
    { key: "stream_version", label: "Version", type: "text", category: "system" },
    { key: "stream_version_type", label: "Versions-Typ", type: "select", options: ["Current", "Draft"], category: "system" },
    { key: "auto_deployment_status", label: "Auto-Deploy Status", type: "select", options: ["Finished", "Released"], category: "system" },
    { key: "schedule_rules_merge_type", label: "Sched. Merge Typ", type: "select", options: ["FromNew", "Merge"], category: "system" },
];

const DEPENDENCY_PARAMS: ParameterConfig[] = [
    { key: "external_dependency_stream", label: "Ext. Abhängigkeit (Stream)", type: "text", category: "dependency" },
    { key: "external_dependency_job", label: "Ext. Abhängigkeit (Job)", type: "text", category: "dependency" },
    { key: "external_dependency_type", label: "Typ", type: "select", options: ["Success", "Failure", "Complete"], category: "dependency" },
    { key: "file_dependency_path", label: "Datei-Trigger Pfad", type: "text", category: "dependency" },
    { key: "file_dependency_condition", label: "Bedingung", type: "select", options: ["Exists", "Missing"], category: "dependency" },
    { key: "file_dependency_interval", label: "Prüfintervall (sek)", type: "number", category: "dependency" },
];

const ALL_STANDARD_JOB_PARAMS: ParameterConfig[] = [
    { key: "agent_detail", label: "Agent / Server", type: "text", category: "job" },
    { key: "run_as_user", label: "Ausführen als User", type: "text", category: "job" },
    { key: "script_type", label: "Script-Typ", type: "select", options: ["Windows", "Unix", "Python", "PowerShell", "Lua", "Shell"], category: "job" },
    { key: "main_script", label: "Script / Befehl", type: "textarea", category: "job" },
    { key: "job_timeout", label: "Timeout (Minuten)", type: "number", category: "job" },
    { key: "retry_count", label: "Wiederholungen", type: "number", category: "job" },
    { key: "job_severity_group", label: "Severity Gruppe", type: "text", category: "job" },
    { key: "job_hold_flag", label: "Job halten", type: "boolean", category: "job" },
    { key: "bypass_status", label: "Bypass", type: "boolean", category: "job" },
];

const ALL_FT_JOB_PARAMS: ParameterConfig[] = [
    { key: "source_agent", label: "Quell-Agent", type: "text", category: "job" },
    { key: "source_file_pattern", label: "Quell-Dateipfad", type: "text", category: "job" },
    { key: "target_agent", label: "Ziel-Agent", type: "text", category: "job" },
    { key: "target_file_path", label: "Ziel-Verzeichnis", type: "text", category: "job" },
    { key: "transfer_mode", label: "Modus", type: "select", options: ["BINARY", "ASCII"], category: "job" },
    { key: "overwrite_target", label: "Ziel überschreiben", type: "select", options: ["YES", "NO"], category: "job" },
    { key: "source_file_delete_flag", label: "Quelldatei löschen", type: "boolean", category: "job" },
    { key: "source_login_object", label: "Quelle Login", type: "text", category: "job" },
    { key: "target_login_object", label: "Ziel Login", type: "text", category: "job" },
    { key: "job_severity_group", label: "Severity Gruppe", type: "text", category: "job" },
];

const ALL_SAP_JOB_PARAMS: ParameterConfig[] = [
    { key: "sap_system", label: "SAP-System", type: "text", category: "job" },
    { key: "sap_client", label: "Mandant", type: "text", category: "job" },
    { key: "sap_user", label: "SAP User", type: "text", category: "job" },
    { key: "sap_report", label: "Report", type: "text", category: "job" },
    { key: "sap_variant", label: "Variante", type: "text", category: "job" },
    { key: "sap_jobname", label: "Jobname (SAP)", type: "text", category: "job" },
    { key: "job_severity_group", label: "Severity Gruppe", type: "text", category: "job" },
];

const ALL_SCHEDULE_PARAMS: ParameterConfig[] = [
    { key: "schedule", label: "Frequenz", type: "select", options: ["einmalig", "täglich", "wöchentlich", "monatlich"], category: "schedule" },
    { key: "start_time", label: "Startzeit", type: "time", category: "schedule" },
    { key: "start_date", label: "Startdatum", type: "text", category: "schedule" },
    { key: "calendar_id", label: "Kalender", type: "text", category: "schedule" },
    { key: "time_zone", label: "Zeitzone", type: "select", options: ["CET", "UTC", "PST", "EST"], category: "schedule" },
];

const ALL_CONTACT_PARAMS: ParameterConfig[] = [
    { key: "contact_first_name", label: "Vorname", type: "text", category: "contact" },
    { key: "contact_last_name", label: "Nachname", type: "text", category: "contact" },
    { key: "contact_email", label: "Email", type: "text", category: "contact" },
    { key: "company_name", label: "Firma", type: "text", category: "contact" },
    { key: "department", label: "Abteilung", type: "text", category: "contact" },
    { key: "contact_type", label: "Kontakt Rolle", type: "select", options: ["Owner", "Notification", "None"], category: "contact" },
    { key: "notify_on_error", label: "Benachrichtigung bei Fehler", type: "select", options: ["YES", "NO"], category: "contact" },
];

export default function StreamDetailPage() {
    const params = useParams();
    const router = useRouter();
    const sessionId = params.id as string;

    const [session, setSession] = useState<SessionData | null>(null);
    const [editedParams, setEditedParams] = useState<Record<string, string | number | boolean>>({});
    const [xmlPreview, setXmlPreview] = useState<string>("");
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [aiInput, setAiInput] = useState("");
    const [isAiProcessing, setIsAiProcessing] = useState(false);
    const [lastAiResponse, setLastAiResponse] = useState<string>("");
    const [validationErrors, setValidationErrors] = useState<string[]>([]);
    const [showSystemParams, setShowSystemParams] = useState(false);

    // Debounce reference
    const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        if (sessionId) {
            loadSession();
        }
    }, [sessionId]);

    const loadSession = async () => {
        setIsLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/api/wizard/sessions/${sessionId}`);
            if (res.ok) {
                const data = await res.json();
                setSession({
                    id: sessionId,
                    name: data.params.stream_name || "Entwurf",
                    status: data.status || "complete",
                    params: data.params,
                    job_type: data.detected_job_type || "STANDARD",
                });
                setEditedParams(data.params);
                validateParams(data.params, data.detected_job_type || "STANDARD");
                // Generate initial XML preview
                generateXmlPreview(data.params, data.detected_job_type);
            }
        } catch (error) {
            console.error("Error loading session:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const validateParams = (currentParams: Record<string, unknown>, jobType: string) => {
        const errors: string[] = [];
        const required = ["stream_name", "short_description"];

        if (jobType === "STANDARD") required.push("agent_detail", "script_type", "main_script");
        if (jobType === "FILE_TRANSFER") required.push("source_agent", "target_agent", "source_file_pattern", "target_file_path");
        if (jobType === "SAP") required.push("sap_system", "sap_client", "sap_report");

        required.forEach(field => {
            if (!currentParams[field]) {
                // Determine label if possible
                const label = field.replace(/_/g, " ").toUpperCase();
                errors.push(`Fehlender Wert: ${label}`);
            }
        });

        setValidationErrors(errors);
        return errors.length === 0;
    };

    const generateXmlPreview = async (paramsToUse: Record<string, unknown>, jobType?: string) => {
        setIsGenerating(true);
        try {
            // First autosave
            await fetch(`http://localhost:8000/api/wizard/sessions/${sessionId}/autosave`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ params: paramsToUse }),
            });

            // Then generate
            const resGen = await fetch(`http://localhost:8000/api/xml/generate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: sessionId }),
            });

            if (resGen.ok) {
                const data = await resGen.json();
                setXmlPreview(data.xml || "<!-- Keine XML-Vorschau verfügbar -->");
            }
        } catch {
            setXmlPreview("<!-- Fehler beim Generieren der XML-Vorschau -->");
        } finally {
            setIsGenerating(false);
        }
    };

    const handleParamChange = useCallback((key: string, value: string | number | boolean) => {
        setEditedParams((prev) => {
            const next = { ...prev, [key]: value };

            // Validate immediately
            validateParams(next, session?.job_type || "STANDARD");

            // Debounced XML generation
            if (debounceTimerRef.current) {
                clearTimeout(debounceTimerRef.current);
            }
            debounceTimerRef.current = setTimeout(() => {
                generateXmlPreview(next, session?.job_type || "STANDARD");
            }, 800);

            return next;
        });
    }, [session?.job_type]);

    const handleSave = async () => {
        setIsSaving(true);
        try {
            await fetch(`http://localhost:8000/api/wizard/sessions/${sessionId}/autosave`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ params: editedParams }),
            });
            await generateXmlPreview(editedParams, session?.job_type || "STANDARD");
        } catch (error) {
            console.error("Error saving:", error);
        } finally {
            setIsSaving(false);
        }
    };

    const handleAiInput = async () => {
        if (!aiInput.trim()) return;
        setIsAiProcessing(true);
        setLastAiResponse("");
        try {
            const res = await fetch("http://localhost:8000/api/chat/message", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: aiInput,
                    session_id: sessionId,
                    current_params: editedParams, // Send current state to avoid overwrite
                }),
            });
            if (res.ok) {
                const data = await res.json();

                // Show AI extracted text response
                if (data.response) {
                    setLastAiResponse(data.response);
                }

                if (data.extracted_params) {
                    const newParams = { ...editedParams, ...data.extracted_params };
                    setEditedParams(newParams);
                    validateParams(newParams, session?.job_type || "STANDARD");
                    generateXmlPreview(newParams, session?.job_type || "STANDARD");
                }
            }
            setAiInput("");
        } catch (error) {
            console.error("Error processing AI input:", error);
            setLastAiResponse("Fehler bei der Anfrage.");
        } finally {
            setIsAiProcessing(false);
        }
    };

    const getJobParams = (): ParameterConfig[] => {
        switch (session?.job_type) {
            case "FILE_TRANSFER":
                return ALL_FT_JOB_PARAMS;
            case "SAP":
                return ALL_SAP_JOB_PARAMS;
            default:
                return ALL_STANDARD_JOB_PARAMS;
        }
    };

    const renderParamInput = (config: ParameterConfig) => {
        const rawValue = editedParams[config.key];
        const value = rawValue !== undefined ? rawValue : "";
        const hasError = !value && validationErrors.some(e => e.includes(config.label.toUpperCase()));

        const baseClass = cn(
            "w-full px-2 py-1.5 rounded border focus:outline-none focus:ring-2 focus:ring-[#0082D9]/20 text-xs transition-colors",
            hasError ? "border-red-300 focus:border-red-500 bg-red-50/50" : "border-gray-200 focus:border-[#0082D9]"
        );

        if (config.type === "boolean") {
            return (
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => handleParamChange(config.key, !Boolean(value))}
                        className={cn(
                            "w-9 h-5 rounded-full relative transition-colors duration-200 ease-in-out",
                            value ? "bg-[#0082D9]" : "bg-gray-200"
                        )}
                    >
                        <span className={cn(
                            "block w-3.5 h-3.5 bg-white rounded-full shadow-sm transform transition-transform duration-200 ease-in-out absolute top-0.5 left-0.5",
                            value ? "translate-x-4" : "translate-x-0"
                        )} />
                    </button>
                    <span className="text-[10px] text-gray-500">{value ? "Ja" : "Nein"}</span>
                </div>
            );
        }

        if (config.type === "select") {
            return (
                <select
                    value={String(value)}
                    onChange={(e) => handleParamChange(config.key, e.target.value)}
                    className={baseClass}
                >
                    <option value="">Auswählen...</option>
                    {config.options?.map((opt) => (
                        <option key={opt} value={opt}>{opt}</option>
                    ))}
                </select>
            );
        }

        if (config.type === "textarea") {
            return (
                <textarea
                    value={String(value)}
                    onChange={(e) => handleParamChange(config.key, e.target.value)}
                    className={cn(baseClass, "min-h-[60px] resize-none")}
                    rows={3}
                />
            );
        }

        return (
            <input
                type={config.type === "number" ? "number" : config.type === "time" ? "time" : "text"}
                value={String(value)}
                onChange={(e) => handleParamChange(config.key, config.type === "number" ? Number(e.target.value) : e.target.value)}
                className={baseClass}
            />
        );
    };

    const renderParamSection = (title: string, configs: ParameterConfig[], isSystem = false) => {
        if (isSystem && !showSystemParams) return null;

        return (
            <div className="space-y-3 pb-4">
                <h4 className={cn(
                    "text-[10px] font-bold uppercase tracking-widest pb-1 border-b flex items-center gap-2",
                    isSystem ? "text-purple-400 border-purple-100" : "text-gray-400 border-gray-100"
                )}>
                    {title}
                    {isSystem && <span className="text-[8px] bg-purple-100 text-purple-600 px-1 rounded">SYSTEM</span>}
                </h4>
                <div className="space-y-3">
                    {configs.map((config) => (
                        <div key={config.key}>
                            <div className="flex justify-between items-baseline mb-1">
                                <label className="text-[10px] font-medium text-gray-600 flex items-center gap-1">
                                    {config.label}
                                    {["stream_name", "short_description"].includes(config.key) && (
                                        <span className="text-red-400">*</span>
                                    )}
                                </label>
                                {config.helperText && <span className="text-[9px] text-gray-400 italic">{config.helperText}</span>}
                            </div>
                            {renderParamInput(config)}
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    if (isLoading) {
        return (
            <AppLayout>
                <div className="flex-1 flex items-center justify-center">
                    <div className="w-10 h-10 border-4 border-gray-200 border-t-[#0082D9] rounded-full animate-spin" />
                </div>
            </AppLayout>
        );
    }

    return (
        <AppLayout sessionId={sessionId}>
            {/* Top Bar - Compact */}
            <div className="bg-white border-b border-gray-200 px-4 py-2 flex items-center justify-between flex-shrink-0 h-14 shadow-sm z-10">
                <div className="flex items-center gap-3">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => router.push("/streams")}
                        className="gap-1.5 text-gray-600 hover:text-gray-900"
                    >
                        <ArrowLeft className="w-3.5 h-3.5" />
                        <span className="text-xs font-medium">Zurück</span>
                    </Button>
                    <div className="h-4 w-px bg-gray-200 mx-1" />
                    <div>
                        <h1 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                            <FileCode className="w-4 h-4 text-[#0082D9]" />
                            {session?.name || "Stream"}
                        </h1>
                        <span className="text-[10px] text-gray-500 flex items-center gap-1.5">
                            <span className={cn("w-1.5 h-1.5 rounded-full", validationErrors.length === 0 ? "bg-emerald-500" : "bg-amber-500")} />
                            {session?.job_type}
                        </span>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-[10px] text-gray-400 pr-2">
                        {isGenerating ? "Synchronisiere..." : "Gespeichert"}
                    </span>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleSave}
                        disabled={isSaving}
                        className="gap-1.5 text-xs h-8"
                    >
                        <Save className={cn("w-3.5 h-3.5", isSaving && "animate-pulse")} />
                        Speichern
                    </Button>
                    <a
                        href={`http://localhost:8000/api/xml/download/${sessionId}`}
                        target="_blank"
                        rel="noreferrer"
                        className={cn(
                            "inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all h-8",
                            validationErrors.length > 0
                                ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                                : "bg-[#0082D9] hover:bg-[#0077C8] text-white shadow-sm"
                        )}
                        onClick={(e) => validationErrors.length > 0 && e.preventDefault()}
                    >
                        <Download className="w-3.5 h-3.5" />
                        XML Download
                    </a>
                </div>
            </div>

            {/* Main Content: 2 Columns */}
            <div className="flex-1 flex min-h-0 bg-gray-50/50">

                {/* LEFT COLUMN: Editor & Tools */}
                <div className="flex-[5] flex flex-col border-r border-gray-200 min-w-0">

                    {/* 1. Top: Monaco Editor */}
                    <div className="flex-1 flex flex-col bg-[#1e1e1e] min-h-0 relative">
                        <div className="px-4 py-2 border-b border-[#333] flex items-center justify-between bg-[#252526] h-[37px] flex-shrink-0">
                            <div className="flex items-center gap-2">
                                <Code className="w-3.5 h-3.5 text-gray-400" />
                                <span className="text-xs font-medium text-gray-300">Live Preview</span>
                            </div>
                            {isGenerating && (
                                <span className="text-[10px] text-gray-400 flex items-center gap-1">
                                    <RefreshCw className="w-3 h-3 animate-spin" /> Updating...
                                </span>
                            )}
                        </div>
                        <div className="flex-1 relative">
                            <Editor
                                height="100%"
                                defaultLanguage="xml"
                                value={xmlPreview}
                                theme="vs-dark"
                                options={{
                                    readOnly: true,
                                    minimap: { enabled: false },
                                    fontSize: 12,
                                    scrollBeyondLastLine: false,
                                    lineNumbers: "on",
                                    renderWhitespace: "selection",
                                    fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
                                }}
                            />
                        </div>
                    </div>

                    {/* 2. Bottom: Analysis & AI */}
                    <div className="bg-white border-t border-gray-200 flex flex-col flex-shrink-0" style={{ height: '300px' }}>
                        <div className="flex-1 flex min-h-0">

                            {/* Validation Status */}
                            <div className="w-[280px] flex flex-col border-r border-gray-100 p-4 overflow-hidden bg-gray-50/30">
                                <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                                    <AlertCircle className="w-3 h-3" />
                                    Validierung
                                </h3>
                                <div className="flex-1 overflow-y-auto pr-1">
                                    {validationErrors.length > 0 ? (
                                        <div className="space-y-2">
                                            {validationErrors.map((err, i) => (
                                                <div key={i} className="flex gap-2 p-2 rounded bg-amber-50 border border-amber-100">
                                                    <div className="w-1 h-full bg-amber-400 rounded-full flex-shrink-0" />
                                                    <span className="text-[10px] text-amber-800 leading-tight">{err}</span>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="flex flex-col items-center justify-center h-full text-emerald-600 gap-2 opacity-80">
                                            <CheckCircle2 className="w-8 h-8 opacity-50" />
                                            <span className="text-xs font-medium">Alles korrekt</span>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* AI Assistant */}
                            <div className="flex-1 flex flex-col p-4 bg-white relative">
                                <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                                    <Sparkles className="w-3 h-3 text-[#0082D9]" />
                                    KI-Assistent
                                </h3>

                                <div className="flex-1 flex flex-col gap-2 overflow-hidden">
                                    {/* Response Area */}
                                    {lastAiResponse && (
                                        <div className="bg-blue-50/50 rounded-lg p-3 text-sm text-gray-700 border border-blue-100 overflow-y-auto flex-shrink-0 max-h-[80px]">
                                            <div className="flex gap-2">
                                                <MessageSquare className="w-4 h-4 text-[#0082D9] mt-0.5 flex-shrink-0" />
                                                <div className="prose prose-sm max-w-none">
                                                    <ReactMarkdown>{lastAiResponse}</ReactMarkdown>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Input Area */}
                                    <div className="flex-1 relative min-h-0">
                                        <textarea
                                            value={aiInput}
                                            onChange={(e) => setAiInput(e.target.value)}
                                            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), handleAiInput())}
                                            placeholder="Sage mir, was ich ändern soll (z.B. 'Füge eine Abhängigkeit zu Stream X hinzu')"
                                            className="w-full h-full p-3 pr-10 rounded-lg border border-gray-100 focus:outline-none focus:ring-2 focus:ring-[#0082D9]/10 focus:border-[#0082D9] text-sm resize-none bg-gray-50 custom-scrollbar transition-all"
                                        />
                                        <button
                                            onClick={handleAiInput}
                                            disabled={isAiProcessing || !aiInput.trim()}
                                            className="absolute bottom-3 right-3 p-1.5 rounded-md bg-[#0082D9] text-white hover:bg-[#0077C8] disabled:opacity-50 disabled:bg-gray-200 transition-all shadow-sm"
                                        >
                                            {isAiProcessing ? (
                                                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                                            ) : (
                                                <Send className="w-3.5 h-3.5" />
                                            )}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* RIGHT COLUMN: Parameter Inputs */}
                <div className="flex-[3] flex flex-col bg-white min-w-[360px] border-l border-gray-200 shadow-[0_0_15px_rgba(0,0,0,0.02)] relative z-20">
                    <div className="px-5 py-3 border-b border-gray-100 flex items-center justify-between bg-white bg-opacity-90 backdrop-blur-sm sticky top-0 z-10">
                        <div className="flex items-center gap-2">
                            <Settings className="w-3.5 h-3.5 text-gray-400" />
                            <span className="text-xs font-bold text-gray-700 uppercase tracking-widest">Konfiguration</span>
                        </div>
                        <button
                            onClick={() => setShowSystemParams(!showSystemParams)}
                            className="text-[10px] text-gray-400 hover:text-gray-600 flex items-center gap-1 px-2 py-1 rounded hover:bg-gray-50 transition-all"
                            title={showSystemParams ? "System-Parameter verbergen" : "Alle Parameter anzeigen anzeigen"}
                        >
                            {showSystemParams ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                            System
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto p-5 space-y-8 custom-scrollbar bg-white">
                        {renderParamSection("Basis Daten", ALL_STREAM_PARAMS)}
                        {renderParamSection("Ausführung & Job", getJobParams())}
                        {renderParamSection("Abhängigkeiten", DEPENDENCY_PARAMS)}
                        {renderParamSection("Zeitplan", ALL_SCHEDULE_PARAMS)}
                        {renderParamSection("Benachrichtigung", ALL_CONTACT_PARAMS)}
                        {renderParamSection("Erweiterte Einstellungen", STREAM_ADVANCED_PARAMS)}
                        {renderParamSection("System / Intern via AI", SYSTEM_PARAMS, true)}
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
