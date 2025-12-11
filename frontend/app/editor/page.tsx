"use client";

import { useState, useEffect, useCallback, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, User, Settings, Wrench, Calendar, CheckCircle, ArrowLeft, ArrowRight, MessageCircle, SkipForward, Check, X, Send } from "lucide-react";
import AppLayout from "../components/AppLayout";
import { Button } from "../components/ui/button";
import { cn } from "../utils/cn";
import WizardStep1BasicInfo from "./components/WizardStep1";
import WizardStep2Contact from "./components/WizardStep2";
import WizardStep3JobType from "./components/WizardStep3";
import WizardStep4JobDetails from "./components/WizardStep4";
import WizardStep5Schedule from "./components/WizardStep5";
import WizardStep6Preview from "./components/WizardStep6";

interface WizardSession {
    session_id: string;
    current_step: string;
    completed_steps: string[];
    params: Record<string, string | boolean | number>;
    ai_suggestions: Record<string, string>;
    detected_job_type: string | null;
    completion_percent: number;
}

interface ChatMessage {
    role: "user" | "assistant";
    content: string;
}

const WIZARD_STEPS = [
    { id: "basic_info", label: "Grundinfo", icon: FileText },
    { id: "contact", label: "Kontakt", icon: User },
    { id: "job_type", label: "Job-Typ", icon: Settings },
    { id: "job_details", label: "Details", icon: Wrench },
    { id: "schedule", label: "Zeitplan", icon: Calendar },
    { id: "preview", label: "Vorschau", icon: CheckCircle },
];

function EditorPageContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const sessionIdParam = searchParams.get("session");

    const [session, setSession] = useState<WizardSession | null>(null);
    const [currentStepIndex, setCurrentStepIndex] = useState(0);
    const [skippedSteps, setSkippedSteps] = useState<Set<number>>(new Set());
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [sessionCreated, setSessionCreated] = useState(false);

    // Chat state
    const [showChat, setShowChat] = useState(false);
    const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
    const [chatInput, setChatInput] = useState("");
    const [isChatLoading, setIsChatLoading] = useState(false);

    // Load session if present in URL
    useEffect(() => {
        if (sessionIdParam) {
            fetchSession(sessionIdParam);
        }
    }, [sessionIdParam]);

    const fetchSession = async (id: string) => {
        setIsLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/api/wizard/sessions/${id}`);
            if (res.ok) {
                const data = await res.json();
                setSession(data);
                setSessionCreated(true);
            } else {
                setError("Session konnte nicht geladen werden.");
            }
        } catch (e) {
            setError("Fehler beim Laden der Session.");
        } finally {
            setIsLoading(false);
        }
    };

    // Don't auto-create session on mount - wait for first input
    const createSession = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch("http://localhost:8000/api/wizard/sessions", {
                method: "POST",
            });
            if (!response.ok) throw new Error("Failed to create session");
            const data = await response.json();
            setSession(data);
        } catch {
            setError("Backend nicht erreichbar. Starte es mit: cd backend && python main.py");
        } finally {
            setIsLoading(false);
        }
    };

    const saveStepData = async (stepId: string, data: Record<string, unknown>, shouldAdvance: boolean = true) => {
        setIsLoading(true);
        try {
            let currentSession = session;

            // Create session on first save (lazy creation)
            if (!currentSession) {
                const createResponse = await fetch("http://localhost:8000/api/wizard/sessions", {
                    method: "POST",
                });
                if (!createResponse.ok) throw new Error("Failed to create session");
                currentSession = await createResponse.json();
                setSession(currentSession);
                setSessionCreated(true);
            }

            const response = await fetch(
                `http://localhost:8000/api/wizard/sessions/${currentSession!.session_id}/step/${stepId}`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ data }),
                }
            );
            if (!response.ok) throw new Error("Failed to save step");
            const updatedSession = await response.json();
            setSession(updatedSession);

            // If on preview step (last step), mark as complete and redirect to detail view
            if (stepId === "preview") {
                // Mark session as complete
                await fetch(
                    `http://localhost:8000/api/wizard/sessions/${currentSession!.session_id}/complete`,
                    { method: "POST" }
                );
                // Redirect to stream detail editor
                router.push(`/streams/${currentSession!.session_id}`);
                return;
            }

            if (shouldAdvance && currentStepIndex < WIZARD_STEPS.length - 1) {
                setCurrentStepIndex(currentStepIndex + 1);
            }
        } catch {
            setError("Fehler beim Speichern");
        } finally {
            setIsLoading(false);
        }
    };

    const analyzeDescription = async (description: string) => {
        if (!session) return null;

        try {
            const response = await fetch(
                `http://localhost:8000/api/wizard/sessions/${session.session_id}/analyze`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ description }),
                }
            );
            if (!response.ok) throw new Error("Failed to analyze");
            const result = await response.json();

            const sessionResponse = await fetch(
                `http://localhost:8000/api/wizard/sessions/${session.session_id}`
            );
            if (sessionResponse.ok) {
                const updatedSession = await sessionResponse.json();
                setSession(updatedSession);
            }

            return result;
        } catch {
            return null;
        }
    };

    const generateXml = async () => {
        if (!session) return null;

        setIsLoading(true);
        try {
            const response = await fetch(
                `http://localhost:8000/api/wizard/sessions/${session.session_id}/generate`,
                { method: "POST" }
            );
            if (!response.ok) throw new Error("Failed to generate XML");
            return await response.json();
        } catch {
            setError("Fehler bei der XML-Generierung");
            return null;
        } finally {
            setIsLoading(false);
        }
    };

    const sendChatMessage = async () => {
        if (!chatInput.trim() || !session) return;

        const userMessage = chatInput.trim();
        setChatInput("");
        setChatMessages(prev => [...prev, { role: "user", content: userMessage }]);
        setIsChatLoading(true);

        try {
            const response = await fetch("http://localhost:8000/api/chat/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: userMessage,
                    session_id: session.session_id
                }),
            });

            if (response.ok) {
                const data = await response.json();
                setChatMessages(prev => [...prev, { role: "assistant", content: data.response }]);
            } else {
                setChatMessages(prev => [...prev, { role: "assistant", content: "Fehler bei der Verarbeitung." }]);
            }
        } catch {
            setChatMessages(prev => [...prev, { role: "assistant", content: "Verbindung zum Backend fehlgeschlagen." }]);
        } finally {
            setIsChatLoading(false);
        }
    };

    const goToStep = (index: number) => {
        if (index > currentStepIndex) {
            const newSkipped = new Set(skippedSteps);
            for (let i = currentStepIndex; i < index; i++) {
                if (!session?.completed_steps.includes(WIZARD_STEPS[i].id)) {
                    newSkipped.add(i);
                }
            }
            setSkippedSteps(newSkipped);
        }
        setCurrentStepIndex(index);
    };

    const goToNextStep = () => {
        if (currentStepIndex >= WIZARD_STEPS.length - 1) return;

        if (!session?.completed_steps.includes(WIZARD_STEPS[currentStepIndex].id)) {
            setSkippedSteps(prev => new Set(prev).add(currentStepIndex));
        }
        setCurrentStepIndex(currentStepIndex + 1);
    };

    const skipToPreview = () => {
        const newSkipped = new Set(skippedSteps);
        for (let i = currentStepIndex; i < WIZARD_STEPS.length - 1; i++) {
            if (!session?.completed_steps.includes(WIZARD_STEPS[i].id)) {
                newSkipped.add(i);
            }
        }
        setSkippedSteps(newSkipped);
        setCurrentStepIndex(WIZARD_STEPS.length - 1);
    };

    const currentStep = WIZARD_STEPS[currentStepIndex];

    const renderCurrentStep = () => {
        const commonProps = {
            session,
            onSave: saveStepData,
            isLoading,
        };

        switch (currentStep.id) {
            case "basic_info":
                return <WizardStep1BasicInfo {...commonProps} onAnalyze={analyzeDescription} />;
            case "contact":
                return <WizardStep2Contact {...commonProps} />;
            case "job_type":
                return <WizardStep3JobType {...commonProps} />;
            case "job_details":
                return <WizardStep4JobDetails {...commonProps} />;
            case "schedule":
                return <WizardStep5Schedule {...commonProps} />;
            case "preview":
                return <WizardStep6Preview {...commonProps} onGenerate={generateXml} />;
            default:
                return null;
        }
    };

    return (
        <AppLayout sessionId={session?.session_id || null}>
            <div className="flex-1 flex overflow-hidden gap-4">
                {/* Left: Step Navigation */}
                <aside className="w-[200px] bg-white rounded-2xl border border-gray-100 p-4 flex flex-col flex-shrink-0 shadow-sm">
                    <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4 px-2">
                        Schritte
                    </h3>
                    <nav className="space-y-1 flex-1">
                        {WIZARD_STEPS.map((step, index) => {
                            const Icon = step.icon;
                            const isCompleted = session?.completed_steps.includes(step.id);
                            const isCurrent = index === currentStepIndex;
                            const isSkipped = skippedSteps.has(index);

                            return (
                                <motion.button
                                    key={step.id}
                                    whileHover={{ x: 2 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={() => goToStep(index)}
                                    className={cn(
                                        "w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 text-left cursor-pointer",
                                        isCurrent && "bg-[#0082D9] text-white shadow-lg shadow-[#0082D9]/20",
                                        isCompleted && !isCurrent && "bg-emerald-50 text-emerald-700 hover:bg-emerald-100",
                                        isSkipped && !isCurrent && "bg-gray-50 text-gray-400 hover:bg-gray-100",
                                        !isCurrent && !isCompleted && !isSkipped && "text-gray-500 hover:bg-gray-50"
                                    )}
                                >
                                    <div className={cn(
                                        "w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0",
                                        isCurrent && "bg-white/20",
                                        isCompleted && !isCurrent && "bg-emerald-100",
                                        isSkipped && !isCurrent && "bg-gray-200",
                                        !isCurrent && !isCompleted && !isSkipped && "bg-gray-100"
                                    )}>
                                        {isCompleted && !isCurrent ? (
                                            <Check className="w-3.5 h-3.5 text-emerald-600" />
                                        ) : isSkipped && !isCurrent ? (
                                            <X className="w-3.5 h-3.5 text-gray-400" />
                                        ) : (
                                            <Icon className={cn(
                                                "w-3.5 h-3.5",
                                                isCurrent && "text-white",
                                                !isCurrent && "text-gray-400"
                                            )} />
                                        )}
                                    </div>
                                    <span className={cn(
                                        "text-sm font-medium",
                                        isCurrent && "text-white"
                                    )}>
                                        {step.label}
                                    </span>
                                </motion.button>
                            );
                        })}
                    </nav>

                    {/* Progress */}
                    <div className="mt-4 pt-4 border-t border-gray-100">
                        <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
                            <span>Fortschritt</span>
                            <span className="font-medium">{Math.round(((currentStepIndex + 1) / WIZARD_STEPS.length) * 100)}%</span>
                        </div>
                        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${((currentStepIndex + 1) / WIZARD_STEPS.length) * 100}%` }}
                                transition={{ duration: 0.5, ease: "easeOut" }}
                                className="h-full bg-gradient-to-r from-[#0082D9] to-emerald-500 rounded-full"
                            />
                        </div>
                    </div>
                </aside>

                {/* Center: Main Content */}
                <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
                    {/* Top bar - simplified */}
                    <div className="flex items-center justify-between mb-3 flex-shrink-0">
                        <span className="text-sm font-medium text-gray-600">
                            Schritt {currentStepIndex + 1} / {WIZARD_STEPS.length}: {currentStep.label}
                        </span>

                        <div className="flex items-center gap-2">
                            {currentStepIndex < WIZARD_STEPS.length - 1 && (
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={skipToPreview}
                                    className="gap-2 text-gray-600"
                                >
                                    <SkipForward className="w-4 h-4" />
                                    Zur Vorschau
                                </Button>
                            )}
                            <Button
                                variant={showChat ? "default" : "outline"}
                                size="sm"
                                onClick={() => setShowChat(!showChat)}
                                className={cn("gap-2", showChat && "bg-[#0082D9] text-white")}
                            >
                                <MessageCircle className="w-4 h-4" />
                                KI-Assistent
                            </Button>
                        </div>
                    </div>

                    {/* Error */}
                    <AnimatePresence>
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-3 flex items-center gap-3 flex-shrink-0"
                            >
                                <span>⚠️</span>
                                <span className="text-sm">{error}</span>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Loading */}
                    {isLoading && !session && (
                        <div className="flex justify-center items-center py-16">
                            <div className="w-10 h-10 border-4 border-gray-200 border-t-[#0082D9] rounded-full animate-spin" />
                        </div>
                    )}

                    {/* Scrollable Step Content */}
                    <div className="flex-1 overflow-y-auto min-h-0">
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={currentStepIndex}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                transition={{ duration: 0.25 }}
                                className="bg-white rounded-2xl shadow-soft border border-gray-100 p-6 min-h-full"
                            >
                                {renderCurrentStep()}
                            </motion.div>
                        </AnimatePresence>
                    </div>

                    {/* Fixed Footer Navigation */}
                    <div className="flex-shrink-0 mt-4 bg-white rounded-2xl border border-gray-100 shadow-lg p-4">
                        <div className="flex items-center justify-between">
                            <Button
                                variant="outline"
                                onClick={() => setCurrentStepIndex(Math.max(0, currentStepIndex - 1))}
                                disabled={currentStepIndex === 0}
                                className="gap-2"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                Zurück
                            </Button>

                            {/* Progress indicator */}
                            <div className="flex items-center gap-2">
                                {WIZARD_STEPS.map((_, index) => (
                                    <div
                                        key={index}
                                        className={cn(
                                            "w-2 h-2 rounded-full transition-colors",
                                            index === currentStepIndex
                                                ? "bg-[#0082D9] w-6"
                                                : index < currentStepIndex || session?.completed_steps.includes(WIZARD_STEPS[index].id)
                                                    ? "bg-emerald-500"
                                                    : "bg-gray-200"
                                        )}
                                    />
                                ))}
                            </div>

                            <Button
                                onClick={goToNextStep}
                                disabled={currentStepIndex === WIZARD_STEPS.length - 1}
                                className="gap-2 bg-[#0082D9] hover:bg-[#0077C8]"
                            >
                                Weiter
                                <ArrowRight className="w-4 h-4" />
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Right: Chat Panel */}
                <AnimatePresence>
                    {showChat && (
                        <motion.aside
                            initial={{ width: 0, opacity: 0 }}
                            animate={{ width: 320, opacity: 1 }}
                            exit={{ width: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            className="bg-white rounded-2xl border border-gray-100 flex flex-col overflow-hidden shadow-sm"
                        >
                            <div className="p-4 border-b border-gray-100">
                                <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                                    <MessageCircle className="w-4 h-4 text-[#0082D9]" />
                                    KI-Assistent
                                </h3>
                                <p className="text-xs text-gray-500 mt-1">Fragen Sie mich zu Ihrem Stream</p>
                            </div>

                            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                                {chatMessages.length === 0 && (
                                    <div className="text-center text-gray-400 text-sm py-8">
                                        <MessageCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                        <p>Stellen Sie eine Frage...</p>
                                    </div>
                                )}
                                {chatMessages.map((msg, i) => (
                                    <div
                                        key={i}
                                        className={cn(
                                            "p-3 rounded-xl text-sm max-w-[90%]",
                                            msg.role === "user"
                                                ? "bg-[#0082D9] text-white ml-auto"
                                                : "bg-gray-100 text-gray-900"
                                        )}
                                    >
                                        {msg.content}
                                    </div>
                                ))}
                                {isChatLoading && (
                                    <div className="flex items-center gap-2 text-gray-400 text-sm">
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                                    </div>
                                )}
                            </div>

                            <div className="p-4 border-t border-gray-100">
                                <div className="flex gap-2">
                                    <input
                                        type="text"
                                        value={chatInput}
                                        onChange={(e) => setChatInput(e.target.value)}
                                        onKeyDown={(e) => e.key === "Enter" && sendChatMessage()}
                                        placeholder="Nachricht..."
                                        className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-[#0082D9]"
                                    />
                                    <Button
                                        size="sm"
                                        onClick={sendChatMessage}
                                        disabled={!chatInput.trim() || isChatLoading}
                                        className="bg-[#0082D9] hover:bg-[#0077C8]"
                                    >
                                        <Send className="w-4 h-4" />
                                    </Button>
                                </div>
                            </div>
                        </motion.aside>
                    )}
                </AnimatePresence>
            </div>
        </AppLayout>
    );
}

export default function EditorPage() {
    return (
        <Suspense fallback={
            <div className="flex items-center justify-center h-screen">
                <div className="w-10 h-10 border-4 border-gray-200 border-t-[#0082D9] rounded-full animate-spin" />
            </div>
        }>
            <EditorPageContent />
        </Suspense>
    );
}
