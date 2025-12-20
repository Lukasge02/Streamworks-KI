"use client";

import { useState, useEffect, useCallback, useImperativeHandle, forwardRef } from "react";
import { motion } from "framer-motion";
import {
  Calendar,
  Clock,
  Sparkles,
  CheckCircle2,
  Repeat,
  AlertTriangle,
} from "lucide-react";
import { useOptions } from "../../hooks/useOptions";

interface WizardSession {
  session_id: string;
  params: Record<string, string | boolean | number>;
  ai_suggestions?: Record<string, string>;
}

interface Props {
  session: WizardSession | null;
  onSave: (
    stepId: string,
    data: Record<string, unknown>,
    shouldAdvance?: boolean,
  ) => Promise<void>;
  isLoading: boolean;
}

export interface WizardStepRef {
  getFormData: () => Record<string, unknown>;
}

const SCHEDULE_OPTIONS = [
  { id: "once", label: "Einmalig", icon: "⚡", description: "Manuelle Ausführung" },
  { id: "hourly", label: "Stündlich", icon: "⏰", description: "Jede Stunde" },
  { id: "daily", label: "Täglich", icon: "📅", description: "Jeden Tag" },
  { id: "weekly", label: "Wöchentlich", icon: "📆", description: "Jede Woche" },
  { id: "monthly", label: "Monatlich", icon: "🗓️", description: "Jeden Monat" },
];

const WizardStep5Schedule = forwardRef<WizardStepRef, Props>(({
  session,
  onSave,
  isLoading,
}, ref) => {
  const [schedule, setSchedule] = useState("daily");
  const [startTime, setStartTime] = useState("08:00");
  const [calendarId, setCalendarId] = useState("");
  const [maxRetries, setMaxRetries] = useState(3);
  const [runOnWeekends, setRunOnWeekends] = useState(true);

  const [hasAiSuggestions, setHasAiSuggestions] = useState(false);
  const { options: calendarOptions } = useOptions("calendar");

  // Load from session
  useEffect(() => {
    if (session?.params) {
      if (session.params.schedule) setSchedule(session.params.schedule as string);
      if (session.params.start_time) setStartTime(session.params.start_time as string);
      if (session.params.calendar_id) setCalendarId(session.params.calendar_id as string);
      if (session.params.max_retries) setMaxRetries(session.params.max_retries as number);
      if (session.params.run_on_weekends !== undefined) {
        setRunOnWeekends(session.params.run_on_weekends as boolean);
      }

      setHasAiSuggestions(!!(session.params.schedule || session.ai_suggestions?.schedule));
    }
  }, [session?.params, session?.ai_suggestions]);

  // Map AI suggestions
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

  // Expose getFormData
  const getFormData = useCallback(() => ({
    schedule,
    start_time: startTime,
    calendar_id: calendarId || null,
    max_retries: maxRetries,
    run_on_weekends: runOnWeekends,
    scheduling_required_flag: schedule !== "once",
  }), [schedule, startTime, calendarId, maxRetries, runOnWeekends]);

  useImperativeHandle(ref, () => ({
    getFormData
  }), [getFormData]);

  // Auto-save
  useEffect(() => {
    const timer = setTimeout(() => {
      onSave("schedule", getFormData(), false);
    }, 1500);
    return () => clearTimeout(timer);
  }, [schedule, startTime, calendarId, maxRetries, runOnWeekends, onSave, getFormData]);

  const getSummaryText = () => {
    const texts: Record<string, string> = {
      once: "Der Stream wird einmalig manuell gestartet.",
      hourly: `Der Stream wird stündlich ausgeführt (Start um ${startTime} Uhr).`,
      daily: `Der Stream wird täglich um ${startTime} Uhr ausgeführt.`,
      weekly: `Der Stream wird wöchentlich um ${startTime} Uhr ausgeführt.`,
      monthly: `Der Stream wird monatlich um ${startTime} Uhr ausgeführt.`,
    };
    let text = texts[schedule];
    if (schedule !== "once" && !runOnWeekends) {
      text += " (Nur werktags)";
    }
    if (calendarId) {
      text += ` Feiertage werden gemäß Kalender übersprungen.`;
    }
    return text;
  };

  const inputBaseClass = `
    w-full px-4 py-3 rounded-xl border-2 transition-all duration-200
    bg-white text-gray-900 placeholder:text-gray-400
    focus:outline-none focus:ring-4 focus:ring-emerald-100 focus:border-emerald-500
    hover:border-gray-300
  `;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="relative">
        <div className="absolute -top-2 -left-2 w-16 h-16 bg-gradient-to-br from-emerald-500/20 to-teal-500/10 rounded-full blur-2xl" />
        <div className="relative">
          <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/25">
              <Calendar className="w-5 h-5 text-white" />
            </div>
            Zeitplan
          </h2>
          <p className="text-gray-500">
            Wann und wie oft soll der Stream ausgeführt werden?
          </p>
        </div>
      </div>

      {/* AI Suggestion Banner */}
      {hasAiSuggestions && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl border border-emerald-100"
        >
          <div className="p-1.5 bg-emerald-100 rounded-lg">
            <Sparkles className="w-4 h-4 text-emerald-600" />
          </div>
          <span className="text-sm text-emerald-700">
            Zeitplan aus Ihrer Beschreibung erkannt
          </span>
        </motion.div>
      )}

      {/* Schedule Type Grid */}
      <div>
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
          <Repeat className="w-4 h-4 text-gray-400" />
          Ausführungshäufigkeit
        </label>
        <div className="grid grid-cols-5 gap-3">
          {SCHEDULE_OPTIONS.map((opt) => (
            <motion.button
              key={opt.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setSchedule(opt.id)}
              className={`
                flex flex-col items-center p-4 rounded-xl border-2 transition-all duration-200
                ${schedule === opt.id
                  ? "bg-gradient-to-br from-emerald-500 to-teal-500 text-white border-emerald-500 shadow-lg shadow-emerald-500/25"
                  : "bg-white border-gray-200 hover:border-emerald-300 text-gray-700 hover:bg-emerald-50/30"
                }
              `}
            >
              <span className="text-2xl mb-1">{opt.icon}</span>
              <span className="font-semibold text-sm">{opt.label}</span>
              <span className={`text-xs mt-0.5 ${schedule === opt.id ? 'text-white/80' : 'text-gray-400'}`}>
                {opt.description}
              </span>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Time Settings */}
      {schedule !== "once" && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="grid grid-cols-1 md:grid-cols-2 gap-5"
        >
          {/* Start Time */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Clock className="w-4 h-4 text-gray-400" />
              Startzeit
            </label>
            <input
              type="time"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              className={`${inputBaseClass} ${startTime ? 'border-emerald-300 bg-emerald-50/30' : 'border-gray-200'}`}
            />
          </div>

          {/* Calendar */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Calendar className="w-4 h-4 text-gray-400" />
              Feiertagskalender
            </label>
            <select
              value={calendarId}
              onChange={(e) => setCalendarId(e.target.value)}
              className={`${inputBaseClass} ${calendarId ? 'border-emerald-300 bg-emerald-50/30' : 'border-gray-200'}`}
            >
              <option value="">Kein Kalender (alle Tage)</option>
              {calendarOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Weekend Toggle */}
          <div className="md:col-span-2">
            <label className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
              <input
                type="checkbox"
                checked={runOnWeekends}
                onChange={(e) => setRunOnWeekends(e.target.checked)}
                className="w-5 h-5 rounded border-gray-300 text-emerald-500 focus:ring-emerald-500"
              />
              <div>
                <span className="font-medium text-gray-900">Am Wochenende ausführen</span>
                <p className="text-sm text-gray-500">Stream läuft auch samstags und sonntags</p>
              </div>
            </label>
          </div>

          {/* Max Retries */}
          <div className="md:col-span-2">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <AlertTriangle className="w-4 h-4 text-gray-400" />
              Wiederholungen bei Fehler
              <span className="ml-auto text-sm font-semibold text-gray-900">{maxRetries}x</span>
            </label>
            <input
              type="range"
              min={0}
              max={10}
              value={maxRetries}
              onChange={(e) => setMaxRetries(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-full appearance-none cursor-pointer
                [&::-webkit-slider-thumb]:appearance-none
                [&::-webkit-slider-thumb]:w-5
                [&::-webkit-slider-thumb]:h-5
                [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:bg-emerald-500
                [&::-webkit-slider-thumb]:shadow-lg
                [&::-webkit-slider-thumb]:cursor-pointer
              "
              style={{
                background: `linear-gradient(to right, #10b981 ${maxRetries * 10}%, #e5e7eb ${maxRetries * 10}%)`
              }}
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>Keine</span>
              <span>10 Versuche</span>
            </div>
          </div>
        </motion.div>
      )}

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-start gap-3 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl border border-emerald-200"
      >
        <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-gray-900 block mb-1">Zusammenfassung</span>
          <p className="text-sm text-gray-700">{getSummaryText()}</p>
        </div>
      </motion.div>
    </div>
  );
});

WizardStep5Schedule.displayName = "WizardStep5Schedule";

export default WizardStep5Schedule;
