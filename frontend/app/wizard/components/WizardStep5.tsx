"use client";

import { FloatingInput } from "@/components/ui/floating-input";
import { FloatingSelect } from "@/components/ui/floating-select";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { useOptions } from "@/lib/api/wizard";
import { cn } from "@/lib/utils";
import { Clock, Calendar, RefreshCw } from "lucide-react";

/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

interface WizardStep5Props {
  data: Record<string, any>;
  onChange: (data: Record<string, any>) => void;
}

/* ------------------------------------------------------------------ */
/* Toggle field (duplicated locally to keep steps self-contained)      */
/* ------------------------------------------------------------------ */

function ToggleField({
  id,
  label,
  description,
  checked,
  onChange,
}: {
  id: string;
  label: string;
  description?: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <div className="flex items-start gap-3">
      <button
        id={id}
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={cn(
          "relative mt-0.5 inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2",
          checked ? "bg-accent" : "bg-border-dark"
        )}
      >
        <span
          className={cn(
            "block h-4 w-4 rounded-full bg-white shadow-sm transition-transform",
            checked ? "translate-x-[18px]" : "translate-x-[2px]"
          )}
        />
      </button>
      <div>
        <label
          htmlFor={id}
          className="text-sm font-medium text-primary cursor-pointer"
        >
          {label}
        </label>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Component                                                           */
/* ------------------------------------------------------------------ */

export default function WizardStep5({ data, onChange }: WizardStep5Props) {
  const { data: scheduleOptions, isLoading: scheduleLoading } =
    useOptions("schedule");
  const { data: calendarOptions, isLoading: calendarLoading } =
    useOptions("calendar");

  function update(key: string, value: string) {
    onChange({ ...data, [key]: value });
  }

  function updateBool(key: string, value: boolean) {
    onChange({ ...data, [key]: value });
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-accent" />
          Zeitplan
        </CardTitle>
        <CardDescription>
          Konfigurieren Sie den Ausfuehrungszeitplan fuer den Stream.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* Schedule Frequency */}
        <FloatingSelect
          id="schedule_frequency"
          label="Ausfuehrungsfrequenz"
          value={(data.schedule_frequency as string) ?? ""}
          onChange={(v) => update("schedule_frequency", v)}
          options={scheduleOptions}
          isLoading={scheduleLoading}
          success={!!data.schedule_frequency}
          icon={<RefreshCw className="h-4 w-4" />}
        />

        {/* Start Time */}
        <FloatingInput
          id="start_time"
          type="text"
          label="Startzeit"
          value={(data.start_time as string) ?? ""}
          onChange={(v) => update("start_time", v)}
          icon={<Clock className="h-4 w-4" />}
          helperText="Uhrzeit der geplanten Ausfuehrung (z.B. 08:00)"
          className="max-w-[200px]"
        />

        {/* Calendar */}
        <FloatingSelect
          id="calendar"
          label="Kalender"
          value={(data.calendar as string) ?? ""}
          onChange={(v) => update("calendar", v)}
          options={calendarOptions}
          isLoading={calendarLoading}
          success={!!data.calendar}
          icon={<Calendar className="h-4 w-4" />}
        />

        {/* Toggles */}
        <div className="space-y-4 pt-2">
          <ToggleField
            id="run_on_holidays"
            label="An Feiertagen ausfuehren"
            description="Stream wird auch an Feiertagen gemaess dem gewaehlten Kalender ausgefuehrt."
            checked={!!data.run_on_holidays}
            onChange={(v) => updateBool("run_on_holidays", v)}
          />

          <ToggleField
            id="run_on_weekends"
            label="Am Wochenende ausfuehren"
            description="Stream wird auch an Samstagen und Sonntagen ausgefuehrt."
            checked={!!data.run_on_weekends}
            onChange={(v) => updateBool("run_on_weekends", v)}
          />
        </div>
      </CardContent>
    </Card>
  );
}
