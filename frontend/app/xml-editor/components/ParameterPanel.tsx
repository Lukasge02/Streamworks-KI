"use client";

import { useState, useEffect, useCallback } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useOptions, useSaveStep } from "@/lib/api/wizard";
import { useToast } from "@/components/ui/toast";
import { cn } from "@/lib/utils";
import {
  FileText,
  Users,
  Cog,
  Clock,
  Settings2,
  ChevronDown,
  RefreshCw,
  Loader2,
} from "lucide-react";

/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

interface ParameterPanelProps {
  sessionData: Record<string, any> | undefined;
  sessionId: string;
  onRegenerate: () => void;
  isRegenerating: boolean;
}

/* ------------------------------------------------------------------ */
/* Collapsible Section                                                 */
/* ------------------------------------------------------------------ */

function Section({
  title,
  icon: Icon,
  defaultOpen = true,
  children,
}: {
  title: string;
  icon: React.ElementType;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className={cn(
      "border border-border/60 rounded-md overflow-hidden transition-all duration-200",
      open && "border-l-[3px] border-l-accent"
    )}>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between w-full px-3 py-2.5 text-xs font-semibold text-primary bg-surface-sunken hover:bg-muted transition-colors"
      >
        <span className="flex items-center gap-2">
          <Icon className={cn(
            "h-4 w-4 transition-colors duration-200",
            open ? "text-accent" : "text-muted-foreground"
          )} />
          {title}
        </span>
        <ChevronDown
          className={cn(
            "h-4 w-4 text-muted-foreground transition-transform duration-200",
            open && "rotate-180"
          )}
        />
      </button>
      <div
        className={cn(
          "overflow-hidden transition-all duration-300 ease-in-out",
          open ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0"
        )}
      >
        <div className="px-3 py-3 space-y-3">{children}</div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Compact form fields                                                 */
/* ------------------------------------------------------------------ */

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1">
      <label className="text-xs font-medium text-muted-foreground">
        {label}
      </label>
      {children}
    </div>
  );
}

function CompactInput({
  value,
  onChange,
  placeholder,
  type = "text",
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
}) {
  return (
    <Input
      type={type}
      className="h-8 text-xs"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
    />
  );
}

function CompactSelect({
  value,
  onChange,
  placeholder,
  options,
  isLoading,
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
  options?: { label: string; value: string }[];
  isLoading?: boolean;
}) {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={isLoading}
        className={cn(
          "flex h-8 w-full rounded-md border border-border/70 bg-surface-raised px-2 py-1 text-xs",
          "transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-1",
          "disabled:cursor-not-allowed disabled:opacity-50 appearance-none"
        )}
      >
        <option value="">{placeholder}</option>
        {options?.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {isLoading && (
        <Loader2 className="absolute right-2 top-1/2 h-3 w-3 -translate-y-1/2 animate-spin text-muted-foreground" />
      )}
    </div>
  );
}

function CompactToggle({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-muted-foreground">{label}</span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={cn(
          "relative inline-flex h-4 w-7 shrink-0 cursor-pointer items-center rounded-full transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-1",
          checked ? "bg-accent" : "bg-border-dark"
        )}
      >
        <span
          className={cn(
            "block h-3 w-3 rounded-full bg-white shadow-sm transition-transform",
            checked ? "translate-x-[14px]" : "translate-x-[2px]"
          )}
        />
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Main Component                                                      */
/* ------------------------------------------------------------------ */

export default function ParameterPanel({
  sessionData,
  sessionId,
  onRegenerate,
  isRegenerating,
}: ParameterPanelProps) {
  const toast = useToast();
  const saveStep = useSaveStep(sessionId);

  // Initialize form from session data
  const [form, setForm] = useState<Record<string, any>>({});
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (sessionData && !initialized) {
      const flat: Record<string, any> = {};
      // Merge all steps into flat form
      for (let i = 0; i <= 6; i++) {
        const stepKey = `step_${i}`;
        if (sessionData[stepKey]) {
          Object.entries(sessionData[stepKey]).forEach(([k, v]) => {
            flat[`${i}.${k}`] = v;
          });
        }
      }
      setForm(flat);
      setInitialized(true);
    }
  }, [sessionData, initialized]);

  // Re-initialize when sessionData changes and we already initialized
  useEffect(() => {
    if (sessionData && initialized) {
      const flat: Record<string, any> = {};
      for (let i = 0; i <= 6; i++) {
        const stepKey = `step_${i}`;
        if (sessionData[stepKey]) {
          Object.entries(sessionData[stepKey]).forEach(([k, v]) => {
            flat[`${i}.${k}`] = v;
          });
        }
      }
      setForm(flat);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionData]);

  const get = useCallback(
    (step: number, key: string) => (form[`${step}.${key}`] as string) ?? "",
    [form]
  );

  const getBool = useCallback(
    (step: number, key: string) => !!form[`${step}.${key}`],
    [form]
  );

  function set(step: number, key: string, value: any) {
    setForm((prev) => ({ ...prev, [`${step}.${key}`]: value }));
  }

  // Track dirty state
  const [originalForm, setOriginalForm] = useState<Record<string, any>>({});
  useEffect(() => {
    if (sessionData && initialized) {
      const flat: Record<string, any> = {};
      for (let i = 0; i <= 6; i++) {
        const stepKey = `step_${i}`;
        if (sessionData[stepKey]) {
          Object.entries(sessionData[stepKey]).forEach(([k, v]) => {
            flat[`${i}.${k}`] = v;
          });
        }
      }
      setOriginalForm(flat);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionData]);

  const isDirty = JSON.stringify(form) !== JSON.stringify(originalForm);

  // Options
  const { data: agents, isLoading: agentsLoading } = useOptions("agents");
  const { data: scheduleOptions, isLoading: scheduleLoading } = useOptions("schedule");
  const { data: calendarOptions, isLoading: calendarLoading } = useOptions("calendar");

  const jobType = get(3, "job_type");

  const errorHandlingOptions = [
    { label: "Abbrechen", value: "ABORT" },
    { label: "Wiederholen", value: "RETRY" },
    { label: "Ignorieren", value: "IGNORE" },
  ];

  // Save changed steps and regenerate
  async function handleRegenerate() {
    try {
      // Group changed fields by step
      const changedSteps = new Map<number, Record<string, any>>();

      for (const [key, value] of Object.entries(form)) {
        const [stepStr, ...fieldParts] = key.split(".");
        const step = parseInt(stepStr, 10);
        const field = fieldParts.join(".");

        if (value !== originalForm[key]) {
          if (!changedSteps.has(step)) {
            // Start with existing step data
            const stepKey = `step_${step}`;
            changedSteps.set(step, { ...(sessionData?.[stepKey] ?? {}) });
          }
          changedSteps.get(step)![field] = value;
        }
      }

      // Also save all fields for changed steps (not just changed ones)
      for (const [key, value] of Object.entries(form)) {
        const [stepStr, ...fieldParts] = key.split(".");
        const step = parseInt(stepStr, 10);
        const field = fieldParts.join(".");

        if (changedSteps.has(step)) {
          changedSteps.get(step)![field] = value;
        }
      }

      // Save each changed step
      for (const [step, data] of changedSteps) {
        await saveStep.mutateAsync({ step, data });
      }

      onRegenerate();
    } catch {
      toast.error("Speichern fehlgeschlagen.");
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto scrollbar-thin space-y-3 pb-20">
        <h3 className="text-sm font-semibold text-primary px-1">Parameter</h3>

        {/* 1. Grunddaten */}
        <Section title="Grunddaten" icon={FileText}>
          <Field label="Stream-Name">
            <CompactInput
              value={get(1, "stream_name")}
              onChange={(v) => set(1, "stream_name", v)}
              placeholder="Stream-Name"
            />
          </Field>
          <Field label="Kurzbeschreibung">
            <CompactInput
              value={get(1, "short_description")}
              onChange={(v) => set(1, "short_description", v)}
              placeholder="Kurzbeschreibung"
            />
          </Field>
          <Field label="Dokumentation">
            <textarea
              className="flex w-full rounded-md border border-border/70 bg-surface-raised px-2 py-1.5 text-xs transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-1 resize-none"
              rows={2}
              value={get(1, "documentation")}
              onChange={(e) => set(1, "documentation", e.target.value)}
              placeholder="Dokumentation"
            />
          </Field>
          <Field label="Prioritaet">
            <CompactInput
              value={get(1, "priority")}
              onChange={(v) => set(1, "priority", v)}
              placeholder="z.B. Hoch"
            />
          </Field>
        </Section>

        {/* 2. Kontakt */}
        <Section title="Kontakt" icon={Users}>
          <Field label="Ansprechpartner">
            <CompactInput
              value={get(2, "contact_name")}
              onChange={(v) => set(2, "contact_name", v)}
              placeholder="Name"
            />
          </Field>
          <Field label="E-Mail">
            <CompactInput
              value={get(2, "email")}
              onChange={(v) => set(2, "email", v)}
              placeholder="E-Mail"
              type="email"
            />
          </Field>
          <Field label="Telefon">
            <CompactInput
              value={get(2, "phone")}
              onChange={(v) => set(2, "phone", v)}
              placeholder="Telefon"
            />
          </Field>
          <Field label="Team">
            <CompactInput
              value={get(2, "team")}
              onChange={(v) => set(2, "team", v)}
              placeholder="Team / Abteilung"
            />
          </Field>
        </Section>

        {/* 3. Job-Konfiguration */}
        <Section title="Job-Konfiguration" icon={Cog}>
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Job-Typ:</span>
            <Badge variant={jobType === "SAP" ? "warning" : jobType === "FILE_TRANSFER" ? "success" : "default"}>
              {jobType || "Nicht gesetzt"}
            </Badge>
          </div>

          {jobType === "STANDARD" && (
            <>
              <Field label="Agent">
                <CompactSelect
                  value={get(4, "agent")}
                  onChange={(v) => set(4, "agent", v)}
                  placeholder="Agent auswaehlen..."
                  options={agents}
                  isLoading={agentsLoading}
                />
              </Field>
              <Field label="Hauptskript">
                <CompactInput
                  value={get(4, "main_script")}
                  onChange={(v) => set(4, "main_script", v)}
                  placeholder="/scripts/script.sh"
                />
              </Field>
              <Field label="Skript-Parameter">
                <CompactInput
                  value={get(4, "script_parameters")}
                  onChange={(v) => set(4, "script_parameters", v)}
                  placeholder="--env=prod"
                />
              </Field>
            </>
          )}

          {jobType === "FILE_TRANSFER" && (
            <>
              <Field label="Quell-Agent">
                <CompactSelect
                  value={get(4, "source_agent")}
                  onChange={(v) => set(4, "source_agent", v)}
                  placeholder="Quell-Agent..."
                  options={agents}
                  isLoading={agentsLoading}
                />
              </Field>
              <Field label="Ziel-Agent">
                <CompactSelect
                  value={get(4, "target_agent")}
                  onChange={(v) => set(4, "target_agent", v)}
                  placeholder="Ziel-Agent..."
                  options={agents}
                  isLoading={agentsLoading}
                />
              </Field>
              <Field label="Quell-Dateimuster">
                <CompactInput
                  value={get(4, "source_file_pattern")}
                  onChange={(v) => set(4, "source_file_pattern", v)}
                  placeholder="/data/export/*.csv"
                />
              </Field>
              <Field label="Ziel-Dateipfad">
                <CompactInput
                  value={get(4, "target_file_path")}
                  onChange={(v) => set(4, "target_file_path", v)}
                  placeholder="/data/import/"
                />
              </Field>
              <Field label="Uebertragungsmodus">
                <CompactSelect
                  value={get(4, "transfer_mode")}
                  onChange={(v) => set(4, "transfer_mode", v)}
                  placeholder="Modus..."
                  options={[
                    { label: "Binaer", value: "binary" },
                    { label: "Text / ASCII", value: "text" },
                  ]}
                />
              </Field>
              <CompactToggle
                label="Ueberschreiben"
                checked={getBool(4, "overwrite")}
                onChange={(v) => set(4, "overwrite", v)}
              />
            </>
          )}

          {jobType === "SAP" && (
            <>
              <Field label="SAP-System">
                <CompactSelect
                  value={get(4, "sap_system")}
                  onChange={(v) => set(4, "sap_system", v)}
                  placeholder="System..."
                  options={[
                    { label: "PRD - Produktion", value: "PRD" },
                    { label: "QAS - Qualitaetssicherung", value: "QAS" },
                    { label: "DEV - Entwicklung", value: "DEV" },
                  ]}
                />
              </Field>
              <Field label="Mandant">
                <CompactInput
                  value={get(4, "sap_client")}
                  onChange={(v) => set(4, "sap_client", v)}
                  placeholder="z.B. 100"
                />
              </Field>
              <Field label="Report">
                <CompactInput
                  value={get(4, "sap_report")}
                  onChange={(v) => set(4, "sap_report", v)}
                  placeholder="z.B. ZFINANCE01"
                />
              </Field>
              <Field label="Variante">
                <CompactInput
                  value={get(4, "sap_variant")}
                  onChange={(v) => set(4, "sap_variant", v)}
                  placeholder="z.B. DAILY_RUN"
                />
              </Field>
            </>
          )}
        </Section>

        {/* 4. Zeitplan */}
        <Section title="Zeitplan" icon={Clock}>
          <Field label="Frequenz">
            <CompactSelect
              value={get(5, "schedule_frequency")}
              onChange={(v) => set(5, "schedule_frequency", v)}
              placeholder="Frequenz..."
              options={scheduleOptions}
              isLoading={scheduleLoading}
            />
          </Field>
          <Field label="Startzeit">
            <CompactInput
              value={get(5, "start_time")}
              onChange={(v) => set(5, "start_time", v)}
              placeholder="HH:MM"
              type="time"
            />
          </Field>
          <Field label="Kalender">
            <CompactSelect
              value={get(5, "calendar")}
              onChange={(v) => set(5, "calendar", v)}
              placeholder="Kalender..."
              options={calendarOptions}
              isLoading={calendarLoading}
            />
          </Field>
          <CompactToggle
            label="An Feiertagen"
            checked={getBool(5, "run_on_holidays")}
            onChange={(v) => set(5, "run_on_holidays", v)}
          />
          <CompactToggle
            label="Am Wochenende"
            checked={getBool(5, "run_on_weekends")}
            onChange={(v) => set(5, "run_on_weekends", v)}
          />
        </Section>

        {/* 5. Erweitert */}
        <Section title="Erweitert" icon={Settings2} defaultOpen={false}>
          <Field label="Fehlerbehandlung">
            <CompactSelect
              value={get(4, "error_handling") || ""}
              onChange={(v) => set(4, "error_handling", v)}
              placeholder="Fehlerbehandlung..."
              options={errorHandlingOptions}
            />
          </Field>
          <Field label="Max. Wiederholungen">
            <CompactInput
              value={get(4, "max_retries") || ""}
              onChange={(v) => set(4, "max_retries", v)}
              placeholder="z.B. 3"
            />
          </Field>
          <Field label="Wiederholungsintervall (s)">
            <CompactInput
              value={get(4, "retry_interval") || ""}
              onChange={(v) => set(4, "retry_interval", v)}
              placeholder="z.B. 60"
            />
          </Field>
        </Section>
      </div>

      {/* Sticky bottom button */}
      <div className="sticky bottom-0 border-t border-border/60 bg-surface-raised px-3 py-3">
        <Button
          onClick={handleRegenerate}
          disabled={isRegenerating || saveStep.isPending}
          className="w-full"
          size="sm"
        >
          {isRegenerating || saveStep.isPending ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <RefreshCw className="h-3.5 w-3.5" />
          )}
          {isDirty ? "Speichern & Neu generieren" : "Neu generieren"}
        </Button>
        {isDirty && (
          <p className="text-[10px] text-center text-muted-foreground mt-1">
            Ungespeicherte Aenderungen
          </p>
        )}
      </div>
    </div>
  );
}
