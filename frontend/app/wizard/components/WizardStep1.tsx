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
import { FileText, Hash } from "lucide-react";

/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

interface WizardStep1Props {
  data: Record<string, any>;
  onChange: (data: Record<string, any>) => void;
}

/* ------------------------------------------------------------------ */
/* Component                                                           */
/* ------------------------------------------------------------------ */

export default function WizardStep1({ data, onChange }: WizardStep1Props) {
  function update(key: string, value: string) {
    onChange({ ...data, [key]: value });
  }

  const streamName = (data.stream_name as string) ?? "";
  const nameValid = !streamName || /^[A-Z0-9_]+$/.test(streamName);
  const nameHasValue = streamName.length > 0;

  return (
    <Card>
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
        {/* Stream Name */}
        <FloatingInput
          id="stream_name"
          label="Stream-Name"
          value={streamName}
          onChange={(v) => update("stream_name", v)}
          transformValue={(v) => v.toUpperCase()}
          required
          error={!nameValid ? "Nur Grossbuchstaben, Ziffern und Unterstriche erlaubt." : undefined}
          success={nameValid && nameHasValue}
          helperText="Wird automatisch in Grossbuchstaben umgewandelt"
          icon={<FileText className="h-4 w-4" />}
        />

        {/* Short Description */}
        <FloatingInput
          id="short_description"
          label="Kurzbeschreibung"
          value={(data.short_description as string) ?? ""}
          onChange={(v) => update("short_description", v)}
          maxLength={120}
          helperText="Kurze Zusammenfassung des Stream-Zwecks"
        />

        {/* Documentation */}
        <FloatingTextarea
          id="documentation"
          label="Dokumentation"
          value={(data.documentation as string) ?? ""}
          onChange={(v) => update("documentation", v)}
          rows={4}
          helperText="Detaillierte Beschreibung, Zweck und Abhaengigkeiten"
        />

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
