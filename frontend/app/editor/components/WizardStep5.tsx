"use client";

import { useState, useEffect } from "react";
import { FormField, InputField } from "../../components/ui/FormField";
import { Combobox } from "../../components/ui/Combobox";
import { Clock, Calendar, CheckCircle } from "lucide-react";
import { cn } from "../../utils/cn";
import { useOptions } from "../../hooks/useOptions";

interface WizardSession {
    session_id: string;
    params: Record<string, string | boolean | number>;
    ai_suggestions: Record<string, string>;
}

interface Props {
    session: WizardSession | null;
    onSave: (stepId: string, data: Record<string, unknown>, shouldAdvance?: boolean) => Promise<void>;
    isLoading: boolean;
}

const SCHEDULE_OPTIONS = [
    { id: "once", label: "Einmalig", icon: "⏯️" },
    { id: "hourly", label: "Stündlich", icon: "⏰" },
    { id: "daily", label: "Täglich", icon: "📅" },
    { id: "weekly", label: "Wöchentlich", icon: "📆" },
    { id: "monthly", label: "Monatlich", icon: "🗓️" },
];

export default function WizardStep5Schedule({ session, onSave, isLoading }: Props) {
    const [schedule, setSchedule] = useState(session?.params.schedule as string || "daily");
    const { options: calendarOptions } = useOptions("calendar");
    const [startTime, setStartTime] = useState(session?.params.start_time as string || "08:00");
    const [calendarId, setCalendarId] = useState(session?.params.calendar_id as string || "");

    useEffect(() => {
        if (session?.ai_suggestions?.schedule) {
            const suggestion = session.ai_suggestions.schedule.toLowerCase();
            if (suggestion.includes("täglich") || suggestion.includes("daily")) setSchedule("daily");
            if (suggestion.includes("wöchentlich") || suggestion.includes("weekly")) setSchedule("weekly");
            if (suggestion.includes("monatlich") || suggestion.includes("monthly")) setSchedule("monthly");
            if (suggestion.includes("stündlich") || suggestion.includes("hourly")) setSchedule("hourly");
        }
        if (session?.ai_suggestions?.start_time) {
            setStartTime(session.ai_suggestions.start_time);
        }
    }, [session?.ai_suggestions]);

    // Auto-save effect
    useEffect(() => {
        const timer = setTimeout(() => {
            const hasChanges =
                schedule !== session?.params.schedule ||
                startTime !== session?.params.start_time ||
                calendarId !== session?.params.calendar_id;

            if (hasChanges) {
                onSave("schedule", {
                    schedule,
                    start_time: startTime,
                    calendar_id: calendarId || null,
                    scheduling_required_flag: schedule !== "once",
                }, false);
            }
        }, 1000);
        return () => clearTimeout(timer);
    }, [schedule, startTime, calendarId, onSave, session?.params]);

    const handleContinue = async () => {
        await onSave("schedule", {
            schedule,
            start_time: startTime,
            calendar_id: calendarId || null,
            scheduling_required_flag: schedule !== "once",
        });
    };

    const getSummaryText = () => {
        const texts: Record<string, string> = {
            once: "Der Stream wird einmalig manuell gestartet.",
            hourly: "Der Stream wird stündlich ausgeführt.",
            daily: `Der Stream wird täglich um ${startTime} Uhr ausgeführt.`,
            weekly: `Der Stream wird wöchentlich um ${startTime} Uhr ausgeführt.`,
            monthly: `Der Stream wird monatlich um ${startTime} Uhr ausgeführt.`,
        };
        return texts[schedule] + (calendarId ? ` (Kalender: ${calendarId})` : "");
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-xl font-bold text-gray-900 mb-1">
                    Schritt 5: Zeitplan
                </h2>
                <p className="text-gray-500 text-sm">
                    Wann soll der Stream ausgeführt werden?
                </p>
            </div>

            {/* Schedule Type */}
            <FormField
                label="Ausführungshäufigkeit"
                hint="Wie oft soll der Stream ausgeführt werden? Einmalig bedeutet manuelle Ausführung, die anderen Optionen erstellen einen wiederkehrenden Zeitplan."
            >
                <div className="grid grid-cols-5 gap-3">
                    {SCHEDULE_OPTIONS.map((opt) => (
                        <button
                            key={opt.id}
                            onClick={() => setSchedule(opt.id)}
                            className={cn(
                                "flex flex-col items-center p-4 rounded-xl border-2 transition-all duration-200",
                                schedule === opt.id
                                    ? "bg-[#0082D9] text-white border-[#0082D9] shadow-lg"
                                    : "bg-white border-gray-200 hover:border-gray-300 text-gray-700"
                            )}
                        >
                            <span className="text-xl mb-1">{opt.icon}</span>
                            <span className="font-medium text-sm">{opt.label}</span>
                        </button>
                    ))}
                </div>
            </FormField>

            {/* Time Settings */}
            {schedule !== "once" && (
                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        label="Startzeit"
                        hint="Die Uhrzeit, zu der der Stream an den geplanten Tagen ausgeführt werden soll."
                    >
                        <div className="relative">
                            <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                            <InputField
                                type="time"
                                value={startTime}
                                onChange={(e) => setStartTime(e.target.value)}
                                className="pl-10"
                            />
                        </div>
                    </FormField>

                    <FormField
                        label="Kalender"
                        hint="Optional: Ein Kalender-Objekt für Ausnahmen wie Feiertage oder Betriebsferien. Der Stream wird an diesen Tagen nicht ausgeführt."
                    >
                        <Combobox
                            value={calendarId}
                            onChange={setCalendarId}
                            options={calendarOptions}
                            placeholder="Optional: Kalender auswählen..."
                        />
                    </FormField>
                </div>
            )}

            {/* Summary */}
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-5 h-5 text-emerald-600" />
                    <span className="font-semibold text-gray-900">Zusammenfassung</span>
                </div>
                <p className="text-gray-700 text-sm">{getSummaryText()}</p>
            </div>
        </div>
    );
}
