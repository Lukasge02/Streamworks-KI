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
import { Badge } from "@/components/ui/badge";
import { useAnalyze, type AnalyzeResult } from "@/lib/api/wizard";
import { Sparkles, Loader2, ArrowRight, Lightbulb, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

interface WizardStep0Props {
  data: Record<string, any>;
  onChange: (data: Record<string, any>) => void;
  sessionData?: Record<number, Record<string, any>>;
  onApplyParameters?: (params: Record<string, any>) => void;
}

/* ------------------------------------------------------------------ */
/* Suggestion-to-field mapping                                         */
/* ------------------------------------------------------------------ */

const SUGGESTION_FIELD_MAP: Record<string, { key: string; label: string; placeholder: string }[]> = {
  "agent": [
    { key: "agent_detail", label: "Agent", placeholder: "z.B. WIN_AGENT_01" },
  ],
  "quell": [
    { key: "source_agent", label: "Quell-Agent", placeholder: "z.B. SRC_AGENT" },
    { key: "target_agent", label: "Ziel-Agent", placeholder: "z.B. TGT_AGENT" },
  ],
  "ziel": [
    { key: "target_agent", label: "Ziel-Agent", placeholder: "z.B. TGT_AGENT" },
  ],
  "skript": [
    { key: "main_script", label: "Hauptskript", placeholder: "z.B. /scripts/job.sh" },
  ],
  "kontakt": [
    { key: "contact_name", label: "Ansprechpartner", placeholder: "z.B. Max Mustermann" },
    { key: "contact_email", label: "E-Mail", placeholder: "z.B. max@firma.de" },
  ],
  "ansprechpartner": [
    { key: "contact_name", label: "Ansprechpartner", placeholder: "z.B. Max Mustermann" },
    { key: "contact_email", label: "E-Mail", placeholder: "z.B. max@firma.de" },
  ],
  "zeitplan": [
    { key: "schedule", label: "Frequenz", placeholder: "z.B. taeglich" },
    { key: "start_time", label: "Startzeit", placeholder: "z.B. 08:00" },
  ],
  "startzeit": [
    { key: "start_time", label: "Startzeit", placeholder: "z.B. 08:00" },
  ],
  "frequenz": [
    { key: "schedule", label: "Frequenz", placeholder: "z.B. taeglich" },
  ],
  "kalender": [
    { key: "calendar_id", label: "Kalender", placeholder: "z.B. DEFAULT" },
  ],
  "name": [
    { key: "stream_name", label: "Stream-Name", placeholder: "z.B. GECK003_REPORT" },
  ],
  "stream-name": [
    { key: "stream_name", label: "Stream-Name", placeholder: "z.B. GECK003_REPORT" },
  ],
  "datei": [
    { key: "source_file_pattern", label: "Quell-Dateimuster", placeholder: "z.B. /data/*.csv" },
    { key: "target_file_path", label: "Ziel-Pfad", placeholder: "z.B. /import/" },
  ],
  "sap": [
    { key: "sap_system", label: "SAP-System", placeholder: "z.B. PRD" },
    { key: "sap_report", label: "SAP-Report", placeholder: "z.B. ZFINANCE01" },
  ],
};

function getSuggestedFields(suggestions: string[]): { key: string; label: string; placeholder: string }[] {
  const fields: { key: string; label: string; placeholder: string }[] = [];
  const seenKeys = new Set<string>();

  for (const suggestion of suggestions) {
    const lower = suggestion.toLowerCase();
    for (const [keyword, mappedFields] of Object.entries(SUGGESTION_FIELD_MAP)) {
      if (lower.includes(keyword)) {
        for (const field of mappedFields) {
          if (!seenKeys.has(field.key)) {
            seenKeys.add(field.key);
            fields.push(field);
          }
        }
      }
    }
  }

  return fields;
}

/* ------------------------------------------------------------------ */
/* Component                                                           */
/* ------------------------------------------------------------------ */

export default function WizardStep0({
  data,
  onChange,
  onApplyParameters,
}: WizardStep0Props) {
  const analyze = useAnalyze();
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [additionalParams, setAdditionalParams] = useState<Record<string, string>>({});

  const description = (data.description as string) ?? "";

  async function handleAnalyze() {
    if (!description.trim()) return;
    try {
      const res = await analyze.mutateAsync({ description: description.trim() });
      setResult(res);
      setAdditionalParams({});
    } catch {
      // mutation error handled by react-query
    }
  }

  function handleApply() {
    if (!result) return;
    // Merge AI-extracted params with manually added ones
    const merged = { ...result.parameters };
    for (const [key, value] of Object.entries(additionalParams)) {
      if (value.trim()) {
        merged[key] = value.trim();
      }
    }
    onApplyParameters?.({
      ...merged,
      job_type: result.job_type,
    });
    onChange({ ...data, applied: true });
  }

  /* ---- Confidence color ---- */
  function confidenceVariant(
    c: number
  ): "success" | "warning" | "destructive" {
    if (c >= 0.8) return "success";
    if (c >= 0.5) return "warning";
    return "destructive";
  }

  /* ---- Suggested fields from suggestions ---- */
  const suggestedFields = result?.suggestions
    ? getSuggestedFields(result.suggestions)
    : [];

  // Filter out fields that were already extracted by AI
  const missingFields = suggestedFields.filter(
    (f) => !result?.parameters[f.key] || result.parameters[f.key] === ""
  );

  return (
    <div className="space-y-6">
      {/* Description Input */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-accent" />
            KI-gestuetzte Analyse
          </CardTitle>
          <CardDescription>
            Beschreiben Sie den gewuenschten Stream in eigenen Worten. Die KI
            extrahiert automatisch die relevanten Parameter.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <textarea
            className={cn(
              "flex min-h-[160px] w-full rounded-md border border-border bg-surface-raised px-3 py-2 text-sm",
              "shadow-sm transition-colors placeholder:text-muted-foreground",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-1",
              "disabled:cursor-not-allowed disabled:opacity-50 resize-y"
            )}
            placeholder="Beschreiben Sie den gewuenschten Stream, z.B.: Taeglich um 08:00 Uhr soll ein SAP-Report ZFINANCE01 im System PRD mit Client 100 ausgefuehrt werden. Ansprechpartner ist Max Mustermann aus dem Finanz-Team..."
            value={description}
            onChange={(e) => onChange({ ...data, description: e.target.value })}
            disabled={analyze.isPending}
          />

          <div className="flex items-center gap-3">
            <Button
              onClick={handleAnalyze}
              disabled={!description.trim() || analyze.isPending}
            >
              {analyze.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4" />
              )}
              Analysieren
            </Button>

            {analyze.isError && (
              <span className="text-sm text-destructive">
                Analyse fehlgeschlagen. Bitte versuchen Sie es erneut.
              </span>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <Card className="animate-fade-in">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Analyse-Ergebnis</CardTitle>
              <Badge variant={confidenceVariant(result.confidence)}>
                Konfidenz: {Math.round(result.confidence * 100)}%
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-5">
            {/* Job Type */}
            <div>
              <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Erkannter Job-Typ
              </span>
              <p className="mt-1 font-semibold text-primary">
                {result.job_type}
              </p>
            </div>

            {/* Extracted Parameters */}
            {Object.keys(result.parameters).length > 0 && (
              <div>
                <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Extrahierte Parameter
                </span>
                <div className="mt-2 rounded-md border border-border overflow-hidden">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-muted">
                        <th className="px-3 py-2 text-left font-medium text-muted-foreground">
                          Parameter
                        </th>
                        <th className="px-3 py-2 text-left font-medium text-muted-foreground">
                          Wert
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(result.parameters).map(([key, value]) => (
                        <tr
                          key={key}
                          className="border-t border-border"
                        >
                          <td className="px-3 py-2 font-mono text-xs text-accent">
                            {key}
                          </td>
                          <td className="px-3 py-2">
                            {String(value)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Suggestions */}
            {result.suggestions && result.suggestions.length > 0 && (
              <div>
                <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Vorschlaege
                </span>
                <ul className="mt-2 space-y-1.5">
                  {result.suggestions.map((s, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 text-sm text-muted-foreground"
                    >
                      <Lightbulb className="h-4 w-4 shrink-0 mt-0.5 text-warning" />
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Inline fields for missing parameters */}
            {missingFields.length > 0 && (
              <div>
                <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <Plus className="h-3.5 w-3.5" />
                  Fehlende Angaben ergaenzen
                </span>
                <div className="mt-2 grid gap-3 sm:grid-cols-2">
                  {missingFields.map((field) => (
                    <div key={field.key}>
                      <label
                        htmlFor={`additional_${field.key}`}
                        className="text-xs font-medium text-muted-foreground mb-1 block"
                      >
                        {field.label}
                      </label>
                      <input
                        id={`additional_${field.key}`}
                        type="text"
                        className={cn(
                          "flex h-9 w-full rounded-md border border-border bg-surface-raised px-3 py-1 text-sm",
                          "shadow-sm transition-colors placeholder:text-muted-foreground/60",
                          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-1"
                        )}
                        placeholder={field.placeholder}
                        value={additionalParams[field.key] ?? ""}
                        onChange={(e) =>
                          setAdditionalParams((prev) => ({
                            ...prev,
                            [field.key]: e.target.value,
                          }))
                        }
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Apply Button */}
            <div className="pt-2">
              <Button onClick={handleApply}>
                <ArrowRight className="h-4 w-4" />
                Uebernehmen
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
