"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";
import {
  Eye,
  FileCode2,
  Loader2,
  AlertTriangle,
} from "lucide-react";

/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

type ValidationStatus = 'complete' | 'warning' | 'error' | 'pending';

interface WizardStep6Props {
  data: Record<number, Record<string, any>>;
  onChange: (data: Record<string, any>) => void;
  sessionId: string;
  getValidationStatus?: (stepIndex: number) => ValidationStatus;
  onNavigateToEditor: () => Promise<void>;
}

/* ------------------------------------------------------------------ */
/* Step labels for error messages                                      */
/* ------------------------------------------------------------------ */

const STEP_LABELS: Record<number, string> = {
  1: "Grunddaten",
  2: "Kontakt",
  3: "Job-Typ",
  4: "Parameter",
  5: "Zeitplan",
};

/* ------------------------------------------------------------------ */
/* Summary Section                                                     */
/* ------------------------------------------------------------------ */

interface SummaryRowProps {
  label: string;
  value: string | boolean | undefined | null;
}

function SummaryRow({ label, value }: SummaryRowProps) {
  if (value === undefined || value === null || value === "") return null;

  const display =
    typeof value === "boolean" ? (value ? "Ja" : "Nein") : String(value);

  return (
    <div className="flex items-baseline justify-between py-1.5 border-b border-border last:border-0">
      <span className="text-sm text-muted-foreground shrink-0 mr-4">
        {label}
      </span>
      <span className="text-sm font-medium text-primary text-right">
        {display}
      </span>
    </div>
  );
}

function SummarySection({
  title,
  rows,
}: {
  title: string;
  rows: SummaryRowProps[];
}) {
  const filteredRows = rows.filter(
    (r) => r.value !== undefined && r.value !== null && r.value !== ""
  );
  if (filteredRows.length === 0) return null;

  return (
    <div>
      <h4 className="text-sm font-semibold text-accent mb-2">{title}</h4>
      <div className="rounded-md border border-border bg-surface-sunken px-4">
        {filteredRows.map((r, i) => (
          <SummaryRow key={i} label={r.label} value={r.value} />
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Component                                                           */
/* ------------------------------------------------------------------ */

export default function WizardStep6({
  data,
  onChange,
  sessionId,
  getValidationStatus,
  onNavigateToEditor,
}: WizardStep6Props) {
  const toast = useToast();

  const step1 = data[1] ?? {};
  const step2 = data[2] ?? {};
  const step3 = data[3] ?? {};
  const step4 = data[4] ?? {};
  const step5 = data[5] ?? {};

  const [isNavigating, setIsNavigating] = useState(false);

  // Check which steps have errors
  const incompleteSteps: string[] = [];
  if (getValidationStatus) {
    for (let i = 1; i <= 5; i++) {
      const status = getValidationStatus(i);
      if (status === 'error') {
        incompleteSteps.push(STEP_LABELS[i] || `Schritt ${i}`);
      }
    }
  }
  const hasErrors = incompleteSteps.length > 0;

  async function handleNavigateToEditor() {
    if (hasErrors) return;
    setIsNavigating(true);
    try {
      await onNavigateToEditor();
    } catch {
      toast.error("Navigation zum Editor fehlgeschlagen.");
      setIsNavigating(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5 text-accent" />
            Zusammenfassung
          </CardTitle>
          <CardDescription>
            Ueberpruefen Sie alle eingegebenen Daten vor der XML-Generierung.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          <SummarySection
            title="Grunddaten"
            rows={[
              { label: "Stream-Name", value: step1.stream_name },
              { label: "Kurzbeschreibung", value: step1.short_description },
              { label: "Dokumentation", value: step1.documentation },
              { label: "Prioritaet", value: step1.priority },
            ]}
          />

          <SummarySection
            title="Kontakt"
            rows={[
              { label: "Ansprechpartner", value: step2.contact_name },
              { label: "E-Mail", value: step2.email },
              { label: "Telefon", value: step2.phone },
              { label: "Team", value: step2.team },
            ]}
          />

          <SummarySection
            title="Job-Typ"
            rows={[{ label: "Typ", value: step3.job_type }]}
          />

          {step3.job_type === "STANDARD" && (
            <SummarySection
              title="Standard-Parameter"
              rows={[
                { label: "Agent", value: step4.agent },
                { label: "Hauptskript", value: step4.main_script },
                { label: "Skript-Parameter", value: step4.script_parameters },
              ]}
            />
          )}

          {step3.job_type === "FILE_TRANSFER" && (
            <SummarySection
              title="Dateitransfer-Parameter"
              rows={[
                { label: "Quell-Agent", value: step4.source_agent },
                { label: "Ziel-Agent", value: step4.target_agent },
                { label: "Quell-Dateimuster", value: step4.source_file_pattern },
                { label: "Ziel-Dateipfad", value: step4.target_file_path },
                { label: "Uebertragungsmodus", value: step4.transfer_mode },
                { label: "Ueberschreiben", value: step4.overwrite },
              ]}
            />
          )}

          {step3.job_type === "SAP" && (
            <SummarySection
              title="SAP-Parameter"
              rows={[
                { label: "SAP-System", value: step4.sap_system },
                { label: "Mandant", value: step4.sap_client },
                { label: "Report", value: step4.sap_report },
                { label: "Variante", value: step4.sap_variant },
              ]}
            />
          )}

          <SummarySection
            title="Zeitplan"
            rows={[
              { label: "Frequenz", value: step5.schedule_frequency },
              { label: "Startzeit", value: step5.start_time },
              { label: "Kalender", value: step5.calendar },
              { label: "Feiertage", value: step5.run_on_holidays },
              { label: "Wochenende", value: step5.run_on_weekends },
            ]}
          />
        </CardContent>
      </Card>

      {/* XML Generation - navigate to editor */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileCode2 className="h-5 w-5 text-accent" />
            XML-Export
          </CardTitle>
          <CardDescription>
            Generieren Sie die Streamworks-XML und bearbeiten Sie diese im Editor.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {hasErrors && (
            <div className="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2.5 text-sm text-destructive">
              <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
              <span>
                Folgende Schritte haben fehlende Pflichtfelder:{" "}
                <strong>{incompleteSteps.join(", ")}</strong>
              </span>
            </div>
          )}
          <Button
            onClick={handleNavigateToEditor}
            disabled={isNavigating || hasErrors}
            size="lg"
          >
            {isNavigating ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileCode2 className="h-4 w-4" />
            )}
            XML generieren & Editor oeffnen
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
