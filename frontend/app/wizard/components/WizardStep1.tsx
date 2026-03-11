"use client";

import { FloatingInput } from "@/components/ui/floating-input";
import { FloatingTextarea } from "@/components/ui/floating-textarea";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { FileText, Hash, Wand2 } from "lucide-react";
import { cn } from "@/lib/utils";

/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

interface WizardStep1Props {
  data: Record<string, any>;
  onChange: (data: Record<string, any>) => void;
  jobType?: string;
}

/* ------------------------------------------------------------------ */
/* Component                                                           */
/* ------------------------------------------------------------------ */

export default function WizardStep1({ data, onChange, jobType }: WizardStep1Props) {
  function update(key: string, value: string | boolean) {
    onChange({ ...data, [key]: value });
  }

  const streamName = (data.stream_name as string) ?? "";
  const nameValid = !streamName || /^[A-Z0-9_]+$/.test(streamName);
  const nameHasValue = streamName.length > 0;
  const autoDocumentation = !!data.auto_documentation;

  function generateAutoName() {
    const typeKuerzel: Record<string, string> = {
      STANDARD: "STD",
      FILE_TRANSFER: "FT",
      SAP: "SAP",
    };
    const kuerzel = typeKuerzel[jobType || "STANDARD"] || "JOB";
    const now = new Date();
    const ts = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}_${String(now.getHours()).padStart(2, "0")}${String(now.getMinutes()).padStart(2, "0")}`;
    update("stream_name", `GECK003_${kuerzel}_${ts}`);
  }

  return (
    <Card accent>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-accent" />
          Grunddaten
        </CardTitle>
        <CardDescription>
          Geben Sie die grundlegenden Informationen fuer den Stream ein.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* Stream Name + Auto-Generate — single row */}
        <div>
          <FloatingInput
            id="stream_name"
            label="Stream-Name"
            value={streamName}
            onChange={(v) => update("stream_name", v)}
            transformValue={(v) => v.toUpperCase()}
            required
            error={!nameValid ? "Nur Grossbuchstaben, Ziffern und Unterstriche erlaubt." : undefined}
            success={nameValid && nameHasValue}
            icon={<FileText className="h-4 w-4" />}
          />
          <div className="flex items-center justify-between px-1 mt-1.5">
            <span className="text-xs text-muted-foreground">
              Wird automatisch in Grossbuchstaben umgewandelt
            </span>
            <button
              type="button"
              onClick={generateAutoName}
              className="inline-flex items-center gap-1 text-xs text-accent hover:text-accent/80 font-medium transition-colors"
            >
              <Wand2 className="h-3 w-3" />
              Automatisch generieren
            </button>
          </div>
        </div>

        {/* Short Description */}
        <FloatingInput
          id="short_description"
          label="Kurzbeschreibung"
          value={(data.short_description as string) ?? ""}
          onChange={(v) => update("short_description", v)}
          maxLength={120}
          helperText="Kurze Zusammenfassung des Stream-Zwecks"
        />

        {/* Documentation + Auto-Checkbox — integrated into one block */}
        <div>
          <FloatingTextarea
            id="documentation"
            label="Dokumentation"
            value={(data.documentation as string) ?? ""}
            onChange={(v) => update("documentation", v)}
            rows={4}
            disabled={autoDocumentation}
          />
          <div className="flex items-center justify-between px-1 mt-1.5">
            <span className="text-xs text-muted-foreground">
              Detaillierte Beschreibung, Zweck und Abhaengigkeiten
            </span>
            <label className="inline-flex items-center gap-1.5 cursor-pointer select-none">
              <span className={cn(
                "text-xs font-medium transition-colors",
                autoDocumentation ? "text-accent" : "text-muted-foreground"
              )}>
                Auto
              </span>
              <button
                type="button"
                role="switch"
                aria-checked={autoDocumentation}
                onClick={() => update("auto_documentation", !autoDocumentation)}
                className={cn(
                  "relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors duration-200",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2",
                  autoDocumentation ? "bg-accent" : "bg-border"
                )}
              >
                <span
                  className={cn(
                    "pointer-events-none inline-block h-3.5 w-3.5 rounded-full bg-white shadow-sm transition-transform duration-200",
                    autoDocumentation ? "translate-x-[18px]" : "translate-x-[3px]"
                  )}
                />
              </button>
            </label>
          </div>
        </div>

        {/* Priority */}
        <FloatingInput
          id="priority"
          label="Prioritaet"
          type="number"
          value={(data.priority as string) ?? ""}
          onChange={(v) => update("priority", v)}
          min={1}
          max={10}
          helperText="Wert von 1 (niedrig) bis 10 (hoch)"
          icon={<Hash className="h-4 w-4" />}
          className="max-w-[200px]"
        />
      </CardContent>
    </Card>
  );
}
