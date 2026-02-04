"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { useGenerateXml, type GenerateXmlResult } from "@/lib/api/wizard";
import {
  Eye,
  FileCode2,
  Download,
  Loader2,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
} from "lucide-react";

/* ------------------------------------------------------------------ */
/* Monaco Editor - lazy loaded                                         */
/* ------------------------------------------------------------------ */

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[400px] items-center justify-center rounded-md border border-border bg-surface-sunken">
      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
    </div>
  ),
});

/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

interface WizardStep6Props {
  data: Record<number, Record<string, any>>;
  onChange: (data: Record<string, any>) => void;
  sessionId: string;
}

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
}: WizardStep6Props) {
  const toast = useToast();
  const generateXml = useGenerateXml();
  const [xmlResult, setXmlResult] = useState<GenerateXmlResult | null>(null);

  const step1 = data[1] ?? {};
  const step2 = data[2] ?? {};
  const step3 = data[3] ?? {};
  const step4 = data[4] ?? {};
  const step5 = data[5] ?? {};

  async function handleGenerate() {
    try {
      const result = await generateXml.mutateAsync({ session_id: sessionId });
      setXmlResult(result);
      toast.success("XML erfolgreich generiert.");
    } catch {
      toast.error("XML-Generierung fehlgeschlagen.");
    }
  }

  function handleDownload() {
    if (!xmlResult) return;
    const blob = new Blob([xmlResult.xml], { type: "application/xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = xmlResult.filename || "stream.xml";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success("Download gestartet.");
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

      {/* XML Generation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileCode2 className="h-5 w-5 text-accent" />
            XML-Export
          </CardTitle>
          <CardDescription>
            Generieren Sie die Streamworks-XML-Konfigurationsdatei.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Generate Button */}
          {!xmlResult && (
            <Button
              onClick={handleGenerate}
              disabled={generateXml.isPending}
              size="lg"
            >
              {generateXml.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <FileCode2 className="h-4 w-4" />
              )}
              XML Generieren
            </Button>
          )}

          {generateXml.isError && !xmlResult && (
            <p className="text-sm text-destructive">
              Generierung fehlgeschlagen. Bitte ueberpruefen Sie die
              eingegebenen Daten und versuchen Sie es erneut.
            </p>
          )}

          {/* Result */}
          {xmlResult && (
            <div className="space-y-4 animate-fade-in">
              {/* Status & Actions */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                  <span className="text-sm font-medium text-success">
                    XML erfolgreich generiert
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    onClick={handleGenerate}
                    disabled={generateXml.isPending}
                  >
                    {generateXml.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <FileCode2 className="h-4 w-4" />
                    )}
                    Neu generieren
                  </Button>
                  <Button onClick={handleDownload}>
                    <Download className="h-4 w-4" />
                    Herunterladen
                  </Button>
                  <Link href={`/xml-editor?session=${sessionId}`}>
                    <Button variant="outline">
                      <ExternalLink className="h-4 w-4" />
                      Im Editor oeffnen
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Filename */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">Dateiname:</span>
                <Badge variant="outline">{xmlResult.filename}</Badge>
              </div>

              {/* Warnings */}
              {xmlResult.warnings && xmlResult.warnings.length > 0 && (
                <div className="rounded-md border border-warning/30 bg-warning-light p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="h-4 w-4 text-warning" />
                    <span className="text-sm font-medium text-warning">
                      Hinweise ({xmlResult.warnings.length})
                    </span>
                  </div>
                  <ul className="space-y-1 pl-6">
                    {xmlResult.warnings.map((w, i) => (
                      <li
                        key={i}
                        className="text-sm text-muted-foreground list-disc"
                      >
                        {w}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Monaco Editor */}
              <div className="rounded-md border border-border overflow-hidden">
                <MonacoEditor
                  height="400px"
                  language="xml"
                  value={xmlResult.xml}
                  theme="vs"
                  options={{
                    readOnly: true,
                    minimap: { enabled: false },
                    lineNumbers: "on",
                    scrollBeyondLastLine: false,
                    wordWrap: "on",
                    fontSize: 13,
                    padding: { top: 12, bottom: 12 },
                  }}
                />
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
