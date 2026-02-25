"use client";

import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Cog, Terminal, FolderSync, Database } from "lucide-react";

/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

interface WizardStep3Props {
  data: Record<string, any>;
  onChange: (data: Record<string, any>) => void;
}

/* ------------------------------------------------------------------ */
/* Job Type definitions                                                */
/* ------------------------------------------------------------------ */

const JOB_TYPES = [
  {
    value: "STANDARD",
    label: "Standard",
    description:
      "Allgemeine Automatisierung mit Skript-Ausfuehrung auf einem Agenten. Geeignet fuer Batch-Jobs, Datenverarbeitung und benutzerdefinierte Skripte.",
    icon: Terminal,
  },
  {
    value: "FILE_TRANSFER",
    label: "Dateitransfer",
    description:
      "Dateiuebertragung zwischen Agenten oder Servern. Unterstuetzt verschiedene Protokolle und automatische Ueberschreib-Regeln.",
    icon: FolderSync,
  },
  {
    value: "SAP",
    label: "SAP",
    description:
      "Integration mit SAP-Systemen. Ausfuehrung von ABAP-Reports, Varianten und Transaktionen ueber die SAP-Schnittstelle.",
    icon: Database,
  },
] as const;

/* ------------------------------------------------------------------ */
/* Component                                                           */
/* ------------------------------------------------------------------ */

export default function WizardStep3({ data, onChange }: WizardStep3Props) {
  const selectedType = (data.job_type as string) ?? "";

  function select(value: string) {
    onChange({ ...data, job_type: value });
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Cog className="h-5 w-5 text-accent" />
          <h2 className="text-primary">Job-Typ auswaehlen</h2>
        </div>
        <p className="text-sm text-muted-foreground">
          Waehlen Sie den Typ des Automatisierungs-Jobs. Dies bestimmt die
          verfuegbaren Parameter im naechsten Schritt.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {JOB_TYPES.map((jt) => {
          const Icon = jt.icon;
          const isSelected = selectedType === jt.value;

          return (
            <Card
              key={jt.value}
              className={cn(
                "cursor-pointer card-interactive",
                isSelected
                  ? "border-accent ring-2 ring-accent/30 shadow-elevated"
                  : "border-border hover:border-accent/40"
              )}
              onClick={() => select(jt.value)}
            >
              <CardHeader>
                <div
                  className={cn(
                    "flex h-12 w-12 items-center justify-center rounded-lg transition-colors",
                    isSelected
                      ? "bg-accent text-white"
                      : "bg-muted text-muted-foreground"
                  )}
                >
                  <Icon className="h-6 w-6" />
                </div>
                <CardTitle
                  className={cn(
                    "mt-3 text-base",
                    isSelected && "text-accent"
                  )}
                >
                  {jt.label}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {jt.description}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {!selectedType && (
        <p className="text-sm text-warning">
          Bitte waehlen Sie einen Job-Typ aus, um fortzufahren.
        </p>
      )}
    </div>
  );
}
