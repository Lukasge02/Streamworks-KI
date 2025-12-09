"use client";

import { useState, useEffect } from "react";
import { FormField, InputField, TextAreaField } from "../../components/ui/FormField";
import { Button } from "../../components/ui/button";
import { Search, Sparkles } from "lucide-react";

interface WizardSession {
    session_id: string;
    params: Record<string, string | boolean | number>;
    ai_suggestions: Record<string, string>;
    detected_job_type: string | null;
}

interface AnalysisResult {
    detected_job_type: string | null;
    suggested_params: Record<string, string>;
    confidence: number;
    explanation: string;
}

interface Props {
    session: WizardSession | null;
    onSave: (stepId: string, data: Record<string, unknown>, shouldAdvance?: boolean) => Promise<void>;
    onAnalyze: (description: string) => Promise<AnalysisResult | null>;
    isLoading: boolean;
}

export default function WizardStep1BasicInfo({ session, onSave, onAnalyze, isLoading }: Props) {
    const [streamName, setStreamName] = useState(session?.params.stream_name as string || "");
    const [description, setDescription] = useState(session?.params.short_description as string || "");
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

    useEffect(() => {
        if (session?.params.stream_name) setStreamName(session.params.stream_name as string);
        if (session?.params.short_description) setDescription(session.params.short_description as string);
    }, [session?.params]);

    // Auto-save effect
    useEffect(() => {
        const timer = setTimeout(() => {
            if (streamName && (streamName !== session?.params.stream_name || description !== session?.params.short_description)) {
                onSave("basic_info", {
                    stream_name: streamName,
                    short_description: description,
                    stream_documentation: description,
                }, false);
            }
        }, 1000);

        return () => clearTimeout(timer);
    }, [streamName, description, onSave, session?.params]);

    const handleAnalyze = async () => {
        if (!description.trim()) return;
        setIsAnalyzing(true);
        const result = await onAnalyze(description);
        setAnalysisResult(result);
        setIsAnalyzing(false);
        if (result?.suggested_params?.stream_name && !streamName) {
            setStreamName(result.suggested_params.stream_name);
        }
    };

    const handleContinue = async () => {
        if (!streamName.trim() || !description.trim()) return;
        await onSave("basic_info", {
            stream_name: streamName,
            short_description: description,
            stream_documentation: description,
        });
    };

    const isValid = streamName.trim() && description.trim();

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-xl font-bold text-gray-900 mb-1">
                    Schritt 1: Grundinformationen
                </h2>
                <p className="text-gray-500 text-sm">
                    Geben Sie Ihrem Stream einen Namen und beschreiben Sie, was er tun soll.
                </p>
            </div>

            <div className="space-y-5">
                <FormField
                    label="Stream Name"
                    hint="Ein eindeutiger technischer Name für Ihren Stream, z.B. FT_BACKUP_DAILY oder SAP_REPORT_WEEKLY. Verwenden Sie Großbuchstaben und Unterstriche."
                    required
                >
                    <InputField
                        type="text"
                        value={streamName}
                        onChange={(e) => setStreamName(e.target.value)}
                        placeholder="z.B. FT_BACKUP_DAILY"
                    />
                </FormField>

                <FormField
                    label="Beschreibung"
                    hint="Beschreiben Sie in natürlicher Sprache, was dieser Stream tun soll. Die KI analysiert Ihre Beschreibung und schlägt passende Parameter vor."
                    required
                >
                    <TextAreaField
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="z.B. Ich möchte täglich um 8 Uhr eine Datei von Server A nach Server B kopieren"
                        rows={3}
                    />
                    <div className="flex justify-end mt-2">
                        <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={handleAnalyze}
                            disabled={!description.trim() || isAnalyzing}
                            className="gap-2"
                        >
                            <Search className="w-4 h-4" />
                            {isAnalyzing ? "Analysiere..." : "Beschreibung analysieren"}
                        </Button>
                    </div>
                </FormField>

                {/* AI Analysis Result */}
                {analysisResult && (
                    <div className={`rounded-xl border overflow-hidden ${analysisResult.confidence > 0.5
                        ? "bg-emerald-50/50 border-emerald-200"
                        : "bg-amber-50/50 border-amber-200"
                        }`}>
                        {/* Header */}
                        <div className="bg-white/80 backdrop-blur px-4 py-3 border-b border-gray-100 flex items-center gap-3">
                            <Sparkles className="w-5 h-5 text-[#0082D9]" />
                            <span className="font-semibold text-gray-900">KI-Analyse</span>
                            <span className={`ml-auto text-xs px-2.5 py-1 rounded-full font-medium ${analysisResult.confidence > 0.7
                                ? "bg-emerald-100 text-emerald-700"
                                : "bg-amber-100 text-amber-700"
                                }`}>
                                {Math.round(analysisResult.confidence * 100)}% Gesamt-Konfidenz
                            </span>
                        </div>

                        <div className="p-4 space-y-4">
                            {/* Job Type */}
                            {analysisResult.detected_job_type && (
                                <div className="flex items-center gap-3">
                                    <div className="w-2 h-2 rounded-full bg-emerald-500" title="Hohe Konfidenz" />
                                    <span className="text-sm text-gray-600 w-24">Job-Typ</span>
                                    <span className="bg-[#0082D9] text-white px-3 py-1 rounded-lg text-sm font-medium">
                                        {analysisResult.detected_job_type}
                                    </span>
                                </div>
                            )}

                            {/* Extracted Parameters with confidence */}
                            {analysisResult.suggested_params && Object.keys(analysisResult.suggested_params).length > 0 && (
                                <div className="bg-white rounded-xl p-4 shadow-sm space-y-3">
                                    <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                                        <span>Erkannte Parameter</span>
                                        <div className="flex-1 h-px bg-gray-200" />
                                    </div>
                                    <div className="grid gap-2">
                                        {Object.entries(analysisResult.suggested_params)
                                            .filter(([key]) => !['short_description', 'stream_documentation'].includes(key))
                                            .map(([key, value]) => {
                                                const labels: Record<string, string> = {
                                                    stream_name: "Stream-Name",
                                                    schedule: "Zeitplan",
                                                    start_time: "Startzeit",
                                                    source_agent: "Quell-Agent",
                                                    target_agent: "Ziel-Agent",
                                                    source_file_pattern: "Quell-Dateipfad",
                                                    target_file_path: "Ziel-Verzeichnis",
                                                    agent_detail: "Agent/Server",
                                                    main_script: "Script",
                                                    script_type: "Script-Typ",
                                                    sap_system: "SAP-System",
                                                    sap_report: "SAP-Report",
                                                    sap_client: "Mandant",
                                                    sap_variant: "Variante",
                                                    calendar_id: "Kalender",
                                                };

                                                // Heuristic confidence: explicit values are high, generated ones are medium
                                                const isExplicit = description.toLowerCase().includes(String(value).toLowerCase().substring(0, 4));
                                                const paramConfidence = isExplicit ? "high" : "medium";

                                                return (
                                                    <div key={key} className="flex items-center gap-3 group">
                                                        <div
                                                            className={`w-2 h-2 rounded-full flex-shrink-0 ${paramConfidence === "high" ? "bg-emerald-500" : "bg-amber-400"
                                                                }`}
                                                            title={paramConfidence === "high" ? "Explizit genannt" : "Automatisch erkannt"}
                                                        />
                                                        <span className="text-sm text-gray-500 w-32 flex-shrink-0">
                                                            {labels[key] || key}
                                                        </span>
                                                        <span className="text-sm font-medium text-gray-900 truncate flex-1 bg-gray-50 px-2 py-1 rounded">
                                                            {String(value)}
                                                        </span>
                                                        <span className={`text-xs px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity ${paramConfidence === "high"
                                                            ? "bg-emerald-100 text-emerald-600"
                                                            : "bg-amber-100 text-amber-600"
                                                            }`}>
                                                            {paramConfidence === "high" ? "Explizit" : "Erkannt"}
                                                        </span>
                                                    </div>
                                                );
                                            })}
                                    </div>

                                    {/* Legend */}
                                    <div className="flex items-center gap-4 pt-2 border-t border-gray-100 text-xs text-gray-400">
                                        <div className="flex items-center gap-1.5">
                                            <div className="w-2 h-2 rounded-full bg-emerald-500" />
                                            <span>Explizit genannt</span>
                                        </div>
                                        <div className="flex items-center gap-1.5">
                                            <div className="w-2 h-2 rounded-full bg-amber-400" />
                                            <span>Automatisch erkannt</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>

        </div>
    );
}
