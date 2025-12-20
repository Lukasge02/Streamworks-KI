"use client";

import { useState, useEffect, useCallback, useImperativeHandle, forwardRef } from "react";
import { motion } from "framer-motion";
import {
  FileText,
  Sparkles,
  Tag,
  AlertCircle,
  Wand2,
  Loader2,
} from "lucide-react";
import { Button } from "../../components/ui/button";

interface WizardSession {
  session_id: string;
  params: Record<string, string | boolean | number>;
  ai_suggestions?: Record<string, string>;
  detected_job_type?: string | null;
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

const WizardStep1BasicInfo = forwardRef<WizardStepRef, Props>(({
  session,
  onSave,
  isLoading,
}, ref) => {
  const [streamName, setStreamName] = useState("");
  const [shortDescription, setShortDescription] = useState("");
  const [documentation, setDocumentation] = useState("");
  const [priority, setPriority] = useState(5);

  const [hasAiSuggestions, setHasAiSuggestions] = useState(false);
  const [nameError, setNameError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Load from session
  useEffect(() => {
    if (session?.params) {
      if (session.params.stream_name) setStreamName(session.params.stream_name as string);
      if (session.params.short_description) setShortDescription(session.params.short_description as string);
      if (session.params.stream_documentation) setDocumentation(session.params.stream_documentation as string);
      if (session.params.stream_priority) setPriority(session.params.stream_priority as number);

      setHasAiSuggestions(!!(session.params.stream_name || session.ai_suggestions?.stream_name));
    }
  }, [session?.params, session?.ai_suggestions]);

  // Validate stream name
  useEffect(() => {
    if (!streamName) {
      setNameError(null);
      return;
    }
    const isValid = /^[A-Z][A-Z0-9_]*$/.test(streamName);
    if (!isValid && streamName.length > 0) {
      setNameError("Empfehlung: Großbuchstaben und Unterstriche");
    } else {
      setNameError(null);
    }
  }, [streamName]);

  // Format stream name to uppercase
  const formatStreamName = (value: string) => {
    return value.toUpperCase().replace(/[^A-Z0-9_]/g, "_").replace(/_+/g, "_");
  };

  // Generate descriptions from AI input
  const generateDescriptions = async () => {
    if (!session?.session_id || !session.params.ai_input_text) return;

    setIsGenerating(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/wizard/sessions/${session.session_id}/generate-descriptions`,
        { method: "POST" }
      );
      if (response.ok) {
        const data = await response.json();
        if (data.short_description) setShortDescription(data.short_description);
        if (data.stream_documentation) setDocumentation(data.stream_documentation);
      }
    } catch (error) {
      console.error("Error generating descriptions:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  // Expose getFormData
  const getFormData = useCallback(() => ({
    stream_name: streamName,
    short_description: shortDescription,
    stream_documentation: documentation,
    stream_priority: priority,
  }), [streamName, shortDescription, documentation, priority]);

  useImperativeHandle(ref, () => ({
    getFormData
  }), [getFormData]);

  // Auto-save
  useEffect(() => {
    const timer = setTimeout(() => {
      if (streamName) {
        onSave("basic_info", getFormData(), false);
      }
    }, 1500);
    return () => clearTimeout(timer);
  }, [streamName, shortDescription, documentation, priority, onSave, getFormData]);

  const inputBaseClass = `
    w-full px-4 py-3 rounded-xl border-2 transition-all duration-200
    bg-white text-gray-900 placeholder:text-gray-400
    focus:outline-none focus:ring-4 focus:ring-blue-100 focus:border-[#0082D9]
    hover:border-gray-300
  `;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="relative">
        <div className="absolute -top-2 -left-2 w-16 h-16 bg-gradient-to-br from-blue-500/20 to-cyan-500/10 rounded-full blur-2xl" />
        <div className="relative">
          <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/25">
              <FileText className="w-5 h-5 text-white" />
            </div>
            Grundinformationen
          </h2>
          <p className="text-gray-500">
            Benennen und beschreiben Sie Ihren Stream
          </p>
        </div>
      </div>

      {/* AI Suggestion Banner */}
      {hasAiSuggestions && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl border border-blue-100"
        >
          <div className="p-1.5 bg-blue-100 rounded-lg">
            <Sparkles className="w-4 h-4 text-blue-600" />
          </div>
          <span className="text-sm text-blue-700">
            Parameter aus KI-Analyse vorausgefüllt
          </span>
        </motion.div>
      )}

      {/* Form */}
      <div className="space-y-5">
        {/* Stream Name */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <Tag className="w-4 h-4 text-gray-400" />
            Stream-Name
            <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              type="text"
              value={streamName}
              onChange={(e) => setStreamName(formatStreamName(e.target.value))}
              placeholder="FT_BACKUP_DAILY"
              className={`${inputBaseClass} font-mono ${streamName
                  ? nameError
                    ? 'border-amber-300 bg-amber-50/30'
                    : 'border-emerald-300 bg-emerald-50/30'
                  : 'border-gray-200'
                }`}
            />
            {nameError && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <AlertCircle className="w-5 h-5 text-amber-500" />
              </div>
            )}
          </div>
          <p className="mt-1.5 text-xs text-gray-400">
            Technischer Bezeichner: Großbuchstaben, Zahlen, Unterstriche
          </p>
        </div>

        {/* Short Description + Generate Button */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
              <FileText className="w-4 h-4 text-gray-400" />
              Kurzbeschreibung
            </label>
            {session?.params.ai_input_text && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={generateDescriptions}
                disabled={isGenerating}
                className="text-xs text-[#0082D9] hover:text-[#0077C8] gap-1"
              >
                {isGenerating ? (
                  <><Loader2 className="w-3 h-3 animate-spin" /> Generiere...</>
                ) : (
                  <><Wand2 className="w-3 h-3" /> KI generieren</>
                )}
              </Button>
            )}
          </div>
          <input
            type="text"
            value={shortDescription}
            onChange={(e) => setShortDescription(e.target.value)}
            placeholder="Tägliches Backup der Export-Dateien"
            maxLength={200}
            className={`${inputBaseClass} ${shortDescription ? 'border-emerald-300 bg-emerald-50/30' : 'border-gray-200'
              }`}
          />
          <p className="mt-1.5 text-xs text-gray-400 flex justify-between">
            <span>Einzeilige Zusammenfassung für Listen</span>
            <span>{shortDescription.length} / 200</span>
          </p>
        </div>

        {/* Full Documentation */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <FileText className="w-4 h-4 text-gray-400" />
            Streambeschreibung
          </label>
          <textarea
            value={documentation}
            onChange={(e) => setDocumentation(e.target.value)}
            placeholder="Detaillierte Beschreibung: Was macht dieser Stream, warum existiert er, welche Abhängigkeiten hat er..."
            rows={4}
            className={`${inputBaseClass} resize-none ${documentation ? 'border-emerald-300 bg-emerald-50/30' : 'border-gray-200'
              }`}
          />
          <p className="mt-1.5 text-xs text-gray-400">
            Ausführliche Dokumentation für zukünftige Referenz
          </p>
        </div>

        {/* Priority */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
            Priorität
            <span className="ml-auto text-sm font-semibold text-gray-900">{priority}</span>
          </label>
          <input
            type="range"
            min={1}
            max={10}
            value={priority}
            onChange={(e) => setPriority(Number(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-full appearance-none cursor-pointer
              [&::-webkit-slider-thumb]:appearance-none
              [&::-webkit-slider-thumb]:w-5
              [&::-webkit-slider-thumb]:h-5
              [&::-webkit-slider-thumb]:rounded-full
              [&::-webkit-slider-thumb]:bg-[#0082D9]
              [&::-webkit-slider-thumb]:shadow-lg
              [&::-webkit-slider-thumb]:cursor-pointer
            "
            style={{
              background: `linear-gradient(to right, #0082D9 ${(priority - 1) * 11.11}%, #e5e7eb ${(priority - 1) * 11.11}%)`
            }}
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>Niedrig</span>
            <span>Hoch</span>
          </div>
        </div>
      </div>

      {/* Validation Status */}
      {streamName && !nameError && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-2 px-4 py-3 bg-emerald-50 rounded-xl border border-emerald-200"
        >
          <div className="w-2 h-2 rounded-full bg-emerald-500" />
          <span className="text-sm text-emerald-700">Pflichtfelder ausgefüllt</span>
        </motion.div>
      )}
    </div>
  );
});

WizardStep1BasicInfo.displayName = "WizardStep1BasicInfo";

export default WizardStep1BasicInfo;
