"use client";

import { useState, useCallback, useEffect } from "react";
import { Button } from "../../components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import {
    Sparkles,
    Upload,
    FileSpreadsheet,
    FileText,
    Loader2,
    ChevronDown,
    ChevronUp,
    X,
    Zap,
    CheckCircle2,
    Server,
    User,
    Clock,
    Tag,
    Mail,
    FileCode,
    ArrowRight,
} from "lucide-react";

interface WizardSession {
    session_id: string;
    current_step: string;
    completed_steps: string[];
    params: Record<string, string | boolean | number>;
    ai_suggestions: Record<string, string>;
    detected_job_type: string | null;
    completion_percent: number;
}

interface AnalysisResult {
    detected_job_type: string | null;
    suggested_params: Record<string, string>;
    confidence: number;
    explanation: string;
}

interface FileExtractionResult {
    streams: Array<{
        stream_name: string;
        parameters: Record<string, { value: string; confidence: number; is_explicit: boolean }>;
        job_type: string;
        missing_required: string[];
        row_number: number;
    }>;
    summary: {
        total_streams: number;
        complete_streams: number;
        incomplete_streams: number;
    };
}

interface Props {
    session: WizardSession | null;
    onSave: (stepId: string, data: Record<string, unknown>, shouldAdvance?: boolean) => Promise<void>;
    onAnalyze: (description: string) => Promise<AnalysisResult | null>;
    onCreateSession?: () => Promise<WizardSession | null>;
    isLoading: boolean;
}

// Parameter icons mapping
const PARAM_ICONS: Record<string, React.ElementType> = {
    stream_name: Tag,
    source_agent: Server,
    target_agent: Server,
    contact_name: User,
    contact_email: Mail,
    schedule: Clock,
    start_time: Clock,
    main_script: FileCode,
    default: FileText,
};

export default function WizardStep0Describe({
    session,
    onSave,
    onAnalyze,
    onCreateSession,
    isLoading,
}: Props) {
    const [description, setDescription] = useState("");
    const [showUpload, setShowUpload] = useState(false);
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
    const [extractionResult, setExtractionResult] = useState<FileExtractionResult | null>(null);

    // Load AI input from session on mount
    useEffect(() => {
        if (session?.params) {
            const savedAiInput = session.params.ai_input_text as string || "";
            if (savedAiInput && !description) {
                setDescription(savedAiInput);
            }
            if (session.detected_job_type && !analysisResult) {
                setAnalysisResult({
                    detected_job_type: session.detected_job_type,
                    suggested_params: session.ai_suggestions || {},
                    confidence: 0.85,
                    explanation: "Aus vorheriger Analyse"
                });
            }
        }
    }, [session?.params, session?.detected_job_type, session?.ai_suggestions]);

    const hasInput = description.trim() || uploadedFile;
    const hasResult = analysisResult || extractionResult;

    const handleFileSelect = useCallback((file: File) => {
        const ext = file.name.split(".").pop()?.toLowerCase();
        const validExts = ["xlsx", "xls", "csv", "pdf"];
        if (ext && validExts.includes(ext)) {
            setUploadedFile(file);
            setExtractionResult(null);
        }
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    }, [handleFileSelect]);

    const handleAnalyze = useCallback(async () => {
        setIsAnalyzing(true);
        setAnalysisResult(null);
        setExtractionResult(null);

        try {
            if (uploadedFile) {
                let currentSession = session;
                if (!currentSession && onCreateSession) {
                    currentSession = await onCreateSession();
                }
                if (!currentSession?.session_id) {
                    setIsAnalyzing(false);
                    return;
                }
                const formData = new FormData();
                formData.append("file", uploadedFile);
                const res = await fetch(
                    `http://localhost:8000/api/wizard/sessions/${currentSession.session_id}/extract-from-file`,
                    { method: "POST", body: formData }
                );
                if (res.ok) {
                    const data: FileExtractionResult = await res.json();
                    setExtractionResult(data);
                }
            } else if (description.trim()) {
                const result = await onAnalyze(description);
                setAnalysisResult(result);
            }
        } catch (error) {
            console.error("Analysis error:", error);
        } finally {
            setIsAnalyzing(false);
        }
    }, [uploadedFile, description, session, onCreateSession, onAnalyze]);

    const getParamLabel = (key: string): string => {
        const labels: Record<string, string> = {
            stream_name: "Stream-Name",
            source_agent: "Quell-Server",
            target_agent: "Ziel-Server",
            source_file_pattern: "Quelldatei",
            target_file_path: "Zielpfad",
            contact_name: "Ansprechpartner",
            contact_email: "E-Mail",
            team: "Team",
            schedule: "Zeitplan",
            start_time: "Startzeit",
            short_description: "Kurzbeschreibung",
        };
        return labels[key] || key.replace(/_/g, " ");
    };

    const getJobTypeLabel = (type: string): string => {
        const labels: Record<string, string> = {
            FILE_TRANSFER: "Dateitransfer",
            STANDARD: "Standard Job",
            SAP: "SAP Job",
        };
        return labels[type] || type;
    };

    const getJobTypeColor = (type: string): string => {
        const colors: Record<string, string> = {
            FILE_TRANSFER: "from-blue-500 to-cyan-500",
            STANDARD: "from-purple-500 to-pink-500",
            SAP: "from-amber-500 to-orange-500",
        };
        return colors[type] || "from-gray-500 to-gray-600";
    };

    return (
        <div className="h-full flex gap-6">
            {/* Left Side - Input */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Header */}
                <div className="mb-4">
                    <h2 className="text-xl font-bold text-gray-900 flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#0082D9] to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/25">
                            <Sparkles className="w-4 h-4 text-white" />
                        </div>
                        KI-Analyse
                    </h2>
                    <p className="text-gray-500 text-sm mt-1">
                        Beschreiben Sie Ihren Stream - wir extrahieren automatisch alle Parameter
                    </p>
                </div>

                {/* Text Input */}
                <div className="relative flex-1 min-h-[200px]">
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Was soll Ihr Stream tun?

Beispiel: Täglich um 8 Uhr Dateien von PROD_SERVER nach BACKUP_STORAGE kopieren. Ansprechpartner Max Müller (max@firma.de) vom Team IT Ops."
                        disabled={!!uploadedFile}
                        className={`
                            w-full h-full px-4 py-4 rounded-xl border-2 transition-all duration-200 resize-none
                            text-gray-900 placeholder:text-gray-400 text-sm
                            focus:outline-none focus:ring-4 focus:ring-blue-100 focus:border-[#0082D9]
                            ${uploadedFile ? "bg-gray-50 opacity-50" : "bg-white hover:border-gray-300 border-gray-200"}
                        `}
                    />
                    {description && !uploadedFile && (
                        <span className="absolute bottom-3 right-3 text-xs text-gray-400">
                            {description.length} Zeichen
                        </span>
                    )}
                </div>

                {/* Upload Toggle */}
                <div className="mt-3 flex items-center gap-3">
                    <button
                        onClick={() => setShowUpload(!showUpload)}
                        className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-all text-sm
                            ${showUpload || uploadedFile ? "border-[#0082D9] bg-blue-50 text-[#0082D9]" : "border-gray-200"}
                        `}
                    >
                        <Upload className="w-4 h-4" />
                        <span>{uploadedFile ? uploadedFile.name : "Dokument"}</span>
                        {showUpload ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                    </button>
                    {uploadedFile && (
                        <button onClick={() => { setUploadedFile(null); setExtractionResult(null); }} className="text-xs text-gray-500 hover:text-red-500">
                            Entfernen
                        </button>
                    )}
                </div>

                {/* Upload Area */}
                <AnimatePresence>
                    {showUpload && !uploadedFile && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="overflow-hidden mt-3"
                        >
                            <div
                                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                                onDragLeave={() => setIsDragging(false)}
                                onDrop={handleDrop}
                                className={`border-2 border-dashed rounded-xl p-6 text-center transition-all
                                    ${isDragging ? "border-[#0082D9] bg-blue-50" : "border-gray-200 hover:border-gray-300"}
                                `}
                            >
                                <input
                                    type="file"
                                    accept=".xlsx,.xls,.csv,.pdf"
                                    onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
                                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                />
                                <FileSpreadsheet className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                                <p className="text-sm text-gray-500">Excel, CSV oder PDF</p>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Analyze Button */}
                <Button
                    onClick={handleAnalyze}
                    disabled={!hasInput || isAnalyzing}
                    className={`mt-4 w-full py-5 text-base font-semibold rounded-xl transition-all
                        ${hasInput && !isAnalyzing
                            ? "bg-gradient-to-r from-[#0082D9] to-blue-600 hover:shadow-lg shadow-md"
                            : "bg-gray-100 text-gray-400"
                        }
                    `}
                >
                    {isAnalyzing ? (
                        <><Loader2 className="w-5 h-5 animate-spin mr-2" /> Analysiere...</>
                    ) : (
                        <><Zap className="w-5 h-5 mr-2" /> Parameter analysieren</>
                    )}
                </Button>
            </div>

            {/* Right Side - Results Panel */}
            <AnimatePresence>
                {hasResult && (
                    <motion.div
                        initial={{ width: 0, opacity: 0 }}
                        animate={{ width: 320, opacity: 1 }}
                        exit={{ width: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: "easeOut" }}
                        className="bg-gradient-to-br from-gray-50 to-white rounded-2xl border border-gray-100 overflow-hidden flex flex-col"
                    >
                        {/* Results Header */}
                        <div className="p-4 border-b border-gray-100 bg-white">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center">
                                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-gray-900 text-sm">Erkannte Parameter</h3>
                                    <p className="text-xs text-gray-500">
                                        {analysisResult ? Object.keys(analysisResult.suggested_params).length : 0} gefunden
                                    </p>
                                </div>
                                {analysisResult && (
                                    <span className="ml-auto px-2 py-1 bg-emerald-100 text-emerald-700 text-xs rounded-full font-medium">
                                        {Math.round(analysisResult.confidence * 100)}%
                                    </span>
                                )}
                            </div>
                        </div>

                        {/* Job Type Badge */}
                        {analysisResult?.detected_job_type && (
                            <div className="p-4 border-b border-gray-100">
                                <div className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-gradient-to-r ${getJobTypeColor(analysisResult.detected_job_type)} text-white text-sm font-medium shadow-sm`}>
                                    <Tag className="w-4 h-4" />
                                    {getJobTypeLabel(analysisResult.detected_job_type)}
                                </div>
                            </div>
                        )}

                        {/* Parameters List */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-2">
                            {analysisResult && Object.entries(analysisResult.suggested_params).map(([key, value]) => {
                                const IconComponent = PARAM_ICONS[key] || PARAM_ICONS.default;
                                return (
                                    <div
                                        key={key}
                                        className="flex items-start gap-3 p-3 bg-white rounded-xl border border-gray-100 hover:border-gray-200 transition-all"
                                    >
                                        <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                                            <IconComponent className="w-4 h-4 text-gray-500" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-xs text-gray-500 mb-0.5">{getParamLabel(key)}</p>
                                            <p className="text-sm font-medium text-gray-900 truncate">{value}</p>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>

                        {/* Continue Hint */}
                        <div className="p-4 border-t border-gray-100 bg-white">
                            <p className="text-xs text-gray-500 text-center flex items-center justify-center gap-2">
                                Klicke "Weiter" um Parameter zu bearbeiten
                                <ArrowRight className="w-3 h-3" />
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
