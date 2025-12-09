"use client";

import { useState, useEffect } from "react";
import { Sparkles } from "lucide-react";
import { cn } from "../../utils/cn";

interface WizardSession {
    session_id: string;
    params: Record<string, string | boolean | number>;
    detected_job_type: string | null;
}

interface Props {
    session: WizardSession | null;
    onSave: (stepId: string, data: Record<string, unknown>, shouldAdvance?: boolean) => Promise<void>;
    isLoading: boolean;
}

const JOB_TYPES = [
    {
        id: "STANDARD",
        title: "Standard Job",
        icon: "⚙️",
        description: "Script/Befehl ausführen",
        examples: ["Backup", "Batch", "Monitoring"],
    },
    {
        id: "FILE_TRANSFER",
        title: "Dateitransfer",
        icon: "📁",
        description: "Dateien übertragen",
        examples: ["Backup", "Reports", "Sync"],
    },
    {
        id: "SAP",
        title: "SAP Job",
        icon: "🔷",
        description: "SAP Report/ABAP",
        examples: ["Reports", "ABAP", "Varianten"],
    },
];

export default function WizardStep3JobType({ session, onSave, isLoading }: Props) {
    const [selectedType, setSelectedType] = useState<string | null>(
        session?.detected_job_type || (session?.params.job_type as string) || null
    );

    useEffect(() => {
        if (session?.detected_job_type) {
            setSelectedType(session.detected_job_type);
        }
    }, [session?.detected_job_type]);

    // Auto-save effect
    useEffect(() => {
        if (selectedType && selectedType !== session?.params.job_type) {
            onSave("job_type", { job_type: selectedType }, false);
        }
    }, [selectedType, onSave, session?.params]);

    const handleContinue = async () => {
        if (!selectedType) return;
        await onSave("job_type", { job_type: selectedType });
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-xl font-bold text-gray-900 mb-1">
                    Schritt 3: Job-Typ auswählen
                </h2>
                <p className="text-gray-500 text-sm">
                    Welche Art von Job soll ausgeführt werden?
                </p>
            </div>

            {/* AI Suggestion */}
            {session?.detected_job_type && (
                <div className="inline-flex items-center gap-2 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-full text-sm">
                    <Sparkles className="w-4 h-4 text-emerald-600" />
                    <span>KI-Empfehlung: <strong>{session.detected_job_type}</strong></span>
                </div>
            )}

            {/* Job Type Cards */}
            <div className="grid grid-cols-3 gap-4">
                {JOB_TYPES.map((type) => {
                    const isSelected = selectedType === type.id;
                    const isAiSuggested = session?.detected_job_type === type.id;

                    return (
                        <button
                            key={type.id}
                            onClick={() => setSelectedType(type.id)}
                            className={cn(
                                "relative flex flex-col items-center text-center p-5 rounded-xl border-2 transition-all duration-200",
                                isSelected
                                    ? "bg-[#0082D9] text-white border-[#0082D9] shadow-lg"
                                    : isAiSuggested
                                        ? "bg-white border-emerald-400 hover:border-emerald-500"
                                        : "bg-white border-gray-200 hover:border-gray-300"
                            )}
                        >
                            {isAiSuggested && !isSelected && (
                                <span className="absolute -top-2 -right-2 bg-emerald-500 text-white text-xs px-2 py-0.5 rounded-full">
                                    Empfohlen
                                </span>
                            )}

                            <span className="text-2xl mb-2">{type.icon}</span>
                            <span className="font-semibold text-base mb-1">{type.title}</span>
                            <span className={cn(
                                "text-sm mb-3",
                                isSelected ? "text-white/80" : "text-gray-500"
                            )}>
                                {type.description}
                            </span>
                            <div className="flex flex-wrap gap-1.5 justify-center">
                                {type.examples.map((ex) => (
                                    <span
                                        key={ex}
                                        className={cn(
                                            "text-xs px-2 py-0.5 rounded",
                                            isSelected ? "bg-white/20" : "bg-gray-100"
                                        )}
                                    >
                                        {ex}
                                    </span>
                                ))}
                            </div>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
