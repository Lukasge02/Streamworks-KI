"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useState, useEffect, useCallback } from "react";
import AppLayout from "@/components/AppLayout";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { cn } from "@/lib/utils";
import {
  useWizardSession,
  useCreateSession,
  useSaveStep,
} from "@/lib/api/wizard";
import {
  Loader2,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  FileText,
  Users,
  Cog,
  Settings2,
  Clock,
  Eye,
  Check,
  AlertTriangle,
  X,
} from "lucide-react";

import WizardStep0 from "@/wizard/components/WizardStep0";
import WizardStep1 from "@/wizard/components/WizardStep1";
import WizardStep2 from "@/wizard/components/WizardStep2";
import WizardStep3 from "@/wizard/components/WizardStep3";
import WizardStep4 from "@/wizard/components/WizardStep4";
import WizardStep5 from "@/wizard/components/WizardStep5";
import WizardStep6 from "@/wizard/components/WizardStep6";

/* ------------------------------------------------------------------ */
/* Step definitions                                                    */
/* ------------------------------------------------------------------ */

const STEPS = [
  { label: "KI-Analyse", icon: Sparkles },
  { label: "Grunddaten", icon: FileText },
  { label: "Kontakt", icon: Users },
  { label: "Job-Typ", icon: Cog },
  { label: "Parameter", icon: Settings2 },
  { label: "Zeitplan", icon: Clock },
  { label: "Vorschau", icon: Eye },
] as const;

/* ------------------------------------------------------------------ */
/* Step Validation                                                     */
/* ------------------------------------------------------------------ */

type ValidationStatus = 'complete' | 'warning' | 'error' | 'pending';

interface StepValidation {
  required: string[];
  optional: string[];
}

const STEP_VALIDATION: Record<number, StepValidation> = {
  0: { required: [], optional: [] }, // KI-Analyse - immer OK wenn besucht
  1: { required: ['stream_name'], optional: ['short_description', 'documentation', 'priority'] },
  2: { required: [], optional: ['contact_name', 'email', 'phone', 'team'] },
  3: { required: ['job_type'], optional: [] },
  4: { required: [], optional: [] }, // Dynamisch je nach job_type
  5: { required: [], optional: ['schedule_frequency', 'start_time', 'calendar'] },
  6: { required: [], optional: [] }, // Vorschau - immer OK
};

function getStep4Validation(jobType: string): StepValidation {
  switch (jobType) {
    case 'STANDARD':
      return { required: ['agent'], optional: ['main_script', 'script_parameters'] };
    case 'FILE_TRANSFER':
      return { required: ['source_agent', 'target_agent'], optional: ['source_file_pattern', 'target_file_path'] };
    case 'SAP':
      return { required: ['sap_report'], optional: ['sap_system', 'sap_client', 'sap_variant'] };
    default:
      return { required: [], optional: [] };
  }
}

function getStepValidationStatus(
  stepIndex: number,
  stepData: Record<string, any> | undefined,
  visitedSteps: Set<number>,
  jobType?: string
): ValidationStatus {
  // Nicht besuchte Steps sind pending
  if (!visitedSteps.has(stepIndex)) {
    return 'pending';
  }

  // Step 0 und 6 sind immer OK wenn besucht
  if (stepIndex === 0 || stepIndex === 6) {
    return 'complete';
  }

  const validation = stepIndex === 4
    ? getStep4Validation(jobType || 'STANDARD')
    : STEP_VALIDATION[stepIndex];

  // Wenn keine Daten vorhanden und Pflichtfelder existieren -> error
  if (!stepData || Object.keys(stepData).length === 0) {
    if (validation.required.length > 0) {
      return 'error';
    }
    // Keine Pflichtfelder aber optionale -> warning wenn besucht
    if (validation.optional.length > 0) {
      return 'warning';
    }
    return 'complete';
  }

  // Pflichtfelder pruefen
  const missingRequired = validation.required.filter(
    field => !stepData[field] || stepData[field] === ''
  );

  if (missingRequired.length > 0) {
    return 'error'; // Rot
  }

  // Optionale Felder pruefen
  const missingOptional = validation.optional.filter(
    field => !stepData[field] || stepData[field] === ''
  );

  if (missingOptional.length > 0 && validation.optional.length > 0) {
    return 'warning'; // Orange
  }

  return 'complete'; // Gruen
}

/* ------------------------------------------------------------------ */
/* Vertical Step Indicator (Left Sidebar)                              */
/* ------------------------------------------------------------------ */

function VerticalStepIndicator({
  currentStep,
  onStepClick,
  getValidationStatus,
}: {
  currentStep: number;
  onStepClick: (step: number) => void;
  getValidationStatus: (stepIndex: number) => ValidationStatus;
}) {
  return (
    <nav className="flex flex-col h-full">
      <div className="px-4 py-3 border-b border-border/50">
        <h2 className="text-sm font-semibold text-primary">Stream-Wizard</h2>
        <p className="text-[10px] text-muted-foreground mt-0.5">
          Schritt {currentStep + 1} von {STEPS.length}
        </p>
      </div>
      <ol className="flex-1 flex flex-col py-2">
        {STEPS.map((step, idx) => {
          const Icon = step.icon;
          const isActive = idx === currentStep;
          const status = getValidationStatus(idx);

          // Icon und Farbe basierend auf ValidationStatus
          const getStatusIcon = () => {
            if (isActive) return <Icon className="h-3.5 w-3.5" />;
            switch (status) {
              case 'complete':
                return <Check className="h-3.5 w-3.5" />;
              case 'warning':
                return <AlertTriangle className="h-3.5 w-3.5" />;
              case 'error':
                return <X className="h-3.5 w-3.5" />;
              default:
                return <Icon className="h-3.5 w-3.5" />;
            }
          };

          const getStatusLabel = () => {
            if (isActive) return 'Aktuell';
            switch (status) {
              case 'complete':
                return 'Vollstaendig';
              case 'warning':
                return 'Teilweise';
              case 'error':
                return 'Unvollstaendig';
              default:
                return null;
            }
          };

          return (
            <li key={idx} className="relative">
              <button
                type="button"
                onClick={() => onStepClick(idx)}
                className={cn(
                  "flex items-center gap-3 w-full px-4 py-2.5 text-sm font-medium transition-all duration-200",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-accent",
                  // Aktiver Step
                  isActive && "bg-primary/5 text-primary border-l-[3px] border-l-accent",
                  // Complete (Gruen)
                  !isActive && status === 'complete' && "text-success hover:bg-success-light/50 border-l-[3px] border-l-success/50",
                  // Warning (Orange)
                  !isActive && status === 'warning' && "text-warning hover:bg-warning/10 border-l-[3px] border-l-warning/50",
                  // Error (Rot)
                  !isActive && status === 'error' && "text-destructive hover:bg-destructive/10 border-l-[3px] border-l-destructive/50",
                  // Pending (Grau)
                  !isActive && status === 'pending' && "text-muted-foreground hover:bg-muted hover:text-primary border-l-[3px] border-l-transparent"
                )}
              >
                <span
                  className={cn(
                    "flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold shrink-0 transition-all duration-200",
                    // Aktiver Step
                    isActive && "bg-primary text-white shadow-sm",
                    // Complete (Gruen)
                    !isActive && status === 'complete' && "bg-success/15 text-success",
                    // Warning (Orange)
                    !isActive && status === 'warning' && "bg-warning/15 text-warning",
                    // Error (Rot)
                    !isActive && status === 'error' && "bg-destructive/15 text-destructive",
                    // Pending (Grau)
                    !isActive && status === 'pending' && "bg-muted text-muted-foreground"
                  )}
                >
                  {getStatusIcon()}
                </span>
                <div className="flex flex-col items-start">
                  <span className="leading-tight">{step.label}</span>
                  {getStatusLabel() && (
                    <span className={cn(
                      "text-[10px] font-normal",
                      isActive && "text-muted-foreground",
                      !isActive && status === 'complete' && "text-success/70",
                      !isActive && status === 'warning' && "text-warning/70",
                      !isActive && status === 'error' && "text-destructive/70"
                    )}>
                      {getStatusLabel()}
                    </span>
                  )}
                </div>
              </button>
              {/* Verbindungslinie */}
              {idx < STEPS.length - 1 && (
                <div
                  className={cn(
                    "absolute left-[30px] top-[44px] w-[2px] h-[10px] transition-colors duration-300",
                    status === 'complete' && "bg-success/40",
                    status === 'warning' && "bg-warning/40",
                    status === 'error' && "bg-destructive/40",
                    status === 'pending' && "bg-border"
                  )}
                />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

/* ------------------------------------------------------------------ */
/* Main Wizard (inner component that reads search params)              */
/* ------------------------------------------------------------------ */

function WizardInner() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const toast = useToast();

  const sessionId = searchParams.get("session");

  /* ---- Auto-create session if none provided ---- */
  const createSession = useCreateSession();

  useEffect(() => {
    if (!sessionId && !createSession.isPending) {
      createSession
        .mutateAsync()
        .then((s) => router.replace(`/wizard?session=${s.id}`))
        .catch(() => toast.error("Sitzung konnte nicht erstellt werden."));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  /* ---- Fetch session ---- */
  const {
    data: session,
    isLoading: sessionLoading,
  } = useWizardSession(sessionId);

  /* ---- Step state ---- */
  const [currentStep, setCurrentStep] = useState(0);
  const [stepData, setStepData] = useState<Record<number, Record<string, any>>>(
    {}
  );
  const [visitedSteps, setVisitedSteps] = useState<Set<number>>(new Set([0])); // Step 0 ist initial besucht

  // Hydrate step data from session when loaded
  useEffect(() => {
    if (session?.data) {
      const hydrated: Record<number, Record<string, any>> = {};
      const hydratedVisited = new Set<number>([0]); // Step 0 immer als besucht markieren
      for (let i = 0; i <= 6; i++) {
        const key = `step_${i}`;
        if (session.data[key] && Object.keys(session.data[key]).length > 0) {
          hydrated[i] = session.data[key];
          hydratedVisited.add(i);
        }
      }
      setStepData((prev) => {
        // Only set if we haven't already populated to avoid overwriting user edits
        const hasData = Object.keys(prev).length > 0;
        return hasData ? prev : hydrated;
      });
      setVisitedSteps((prev) => {
        // Only set if we haven't already populated
        return prev.size <= 1 ? hydratedVisited : prev;
      });
    }
  }, [session]);

  /* ---- Save step mutation ---- */
  const saveStep = useSaveStep(sessionId ?? "");

  const handleStepDataChange = useCallback(
    (data: Record<string, any>) => {
      setStepData((prev) => ({ ...prev, [currentStep]: data }));
    },
    [currentStep]
  );

  /* ---- Resolve job type for step 4 ---- */
  const jobType =
    stepData[3]?.job_type ||
    session?.data?.step_3?.job_type ||
    session?.data?.job_type ||
    "STANDARD";

  /* ---- Validation status helper (must be before conditional returns) ---- */
  const getValidationStatusForStep = useCallback(
    (stepIndex: number): ValidationStatus => {
      return getStepValidationStatus(stepIndex, stepData[stepIndex], visitedSteps, jobType);
    },
    [stepData, visitedSteps, jobType]
  );

  /* ---- Navigation ---- */

  async function saveCurrentStep() {
    if (!sessionId) return;
    const data = stepData[currentStep] ?? {};
    try {
      await saveStep.mutateAsync({ step: currentStep, data });
    } catch {
      toast.error("Schritt konnte nicht gespeichert werden.");
      throw new Error("save failed");
    }
  }

  async function goNext() {
    try {
      await saveCurrentStep();
      const nextStep = Math.min(currentStep + 1, STEPS.length - 1);
      setCurrentStep(nextStep);
      setVisitedSteps((prev) => new Set([...prev, nextStep]));
    } catch {
      // error already toasted
    }
  }

  async function goBack() {
    try {
      await saveCurrentStep();
    } catch {
      // continue even if save fails on back navigation
    }
    const prevStep = Math.max(currentStep - 1, 0);
    setCurrentStep(prevStep);
    setVisitedSteps((prev) => new Set([...prev, prevStep]));
  }

  async function goToStep(step: number) {
    if (step === currentStep) return;
    try {
      await saveCurrentStep();
    } catch {
      // continue navigation
    }
    setCurrentStep(step);
    setVisitedSteps((prev) => new Set([...prev, step]));
  }

  /* ---- Loading / Missing session ---- */

  if (!sessionId || sessionLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center py-24">
          <Loader2 className="h-8 w-8 animate-spin text-accent" />
        </div>
      </AppLayout>
    );
  }

  /* ---- Step component map ---- */
  const stepComponents: Record<number, React.ReactNode> = {
    0: (
      <WizardStep0
        data={stepData[0] ?? {}}
        onChange={handleStepDataChange}
        sessionData={stepData}
        onApplyParameters={(params) => {
          // Distribute AI-extracted params across all steps
          setStepData((prev) => {
            const next = { ...prev };

            // Step 1: Grunddaten
            const step1Updates: Record<string, any> = {};
            if (params.stream_name) step1Updates.stream_name = params.stream_name;
            if (params.short_description) step1Updates.short_description = params.short_description;
            if (params.stream_documentation) step1Updates.documentation = params.stream_documentation;
            if (params.documentation) step1Updates.documentation = params.documentation;
            if (params.stream_priority) step1Updates.priority = params.stream_priority;
            if (Object.keys(step1Updates).length > 0) {
              next[1] = { ...prev[1], ...step1Updates };
            }

            // Step 2: Kontakt
            const step2Updates: Record<string, any> = {};
            if (params.contact_name) step2Updates.contact_name = params.contact_name;
            if (params.contact_email) step2Updates.email = params.contact_email;
            if (params.contact_phone) step2Updates.phone = params.contact_phone;
            if (params.team) step2Updates.team = params.team;
            if (Object.keys(step2Updates).length > 0) {
              next[2] = { ...prev[2], ...step2Updates };
            }

            // Step 3: Job-Typ
            if (params.job_type) {
              next[3] = { ...prev[3], job_type: params.job_type };
            }

            // Step 4: Job-spezifische Parameter
            const step4Updates: Record<string, any> = {};
            if (params.agent_detail) step4Updates.agent = params.agent_detail;
            if (params.main_script) step4Updates.main_script = params.main_script;
            if (params.script_parameters) step4Updates.script_parameters = params.script_parameters;
            if (params.source_agent) step4Updates.source_agent = params.source_agent;
            if (params.target_agent) step4Updates.target_agent = params.target_agent;
            if (params.source_file_pattern) step4Updates.source_file_pattern = params.source_file_pattern;
            if (params.target_file_path) step4Updates.target_file_path = params.target_file_path;
            if (params.transfer_mode) step4Updates.transfer_mode = params.transfer_mode;
            if (params.overwrite_existing !== undefined) step4Updates.overwrite = params.overwrite_existing;
            if (params.sap_system) step4Updates.sap_system = params.sap_system;
            if (params.sap_client) step4Updates.sap_client = params.sap_client;
            if (params.sap_report) step4Updates.sap_report = params.sap_report;
            if (params.sap_variant) step4Updates.sap_variant = params.sap_variant;
            if (Object.keys(step4Updates).length > 0) {
              next[4] = { ...prev[4], ...step4Updates };
            }

            // Step 5: Zeitplan
            const step5Updates: Record<string, any> = {};
            if (params.schedule) {
              // Normalize umlauts: AI may return "täglich" but dropdowns use "taeglich"
              const umlautMap: Record<string, string> = {
                "täglich": "taeglich",
                "wöchentlich": "woechentlich",
                "monatlich": "monatlich",
                "stündlich": "stuendlich",
                "einmalig": "einmalig",
              };
              const normalized = umlautMap[params.schedule.toLowerCase()] || params.schedule;
              step5Updates.schedule_frequency = normalized;
            }
            if (params.start_time) step5Updates.start_time = params.start_time;
            if (params.calendar_id) step5Updates.calendar = params.calendar_id;
            if (params.run_on_holidays !== undefined) step5Updates.run_on_holidays = params.run_on_holidays;
            if (params.run_on_weekends !== undefined) step5Updates.run_on_weekends = params.run_on_weekends;
            if (Object.keys(step5Updates).length > 0) {
              next[5] = { ...prev[5], ...step5Updates };
            }

            return next;
          });
          toast.success("Parameter uebernommen.");
        }}
      />
    ),
    1: (
      <WizardStep1
        data={stepData[1] ?? {}}
        onChange={handleStepDataChange}
      />
    ),
    2: (
      <WizardStep2
        data={stepData[2] ?? {}}
        onChange={handleStepDataChange}
      />
    ),
    3: (
      <WizardStep3
        data={stepData[3] ?? {}}
        onChange={handleStepDataChange}
      />
    ),
    4: (
      <WizardStep4
        data={stepData[4] ?? {}}
        onChange={handleStepDataChange}
        jobType={jobType}
      />
    ),
    5: (
      <WizardStep5
        data={stepData[5] ?? {}}
        onChange={handleStepDataChange}
      />
    ),
    6: (
      <WizardStep6
        data={stepData}
        onChange={handleStepDataChange}
        sessionId={sessionId}
        onNavigateToEditor={async () => {
          await saveCurrentStep();
          router.push(`/xml-editor?session=${sessionId}`);
        }}
      />
    ),
  };

  const isFirst = currentStep === 0;
  const isLast = currentStep === STEPS.length - 1;

  return (
    <AppLayout noScroll>
      <div className="flex h-full">
        {/* Left: Vertical Step Navigation */}
        <div className="hidden md:flex w-[220px] flex-col border-r border-border/50 bg-surface-raised shrink-0">
          <VerticalStepIndicator
            currentStep={currentStep}
            onStepClick={goToStep}
            getValidationStatus={getValidationStatusForStep}
          />
        </div>

        {/* Right: Content Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Mobile Step Indicator */}
          <div className="md:hidden flex items-center justify-between px-4 py-3 border-b border-border/50 bg-surface-raised">
            <span className="text-sm font-medium text-primary">
              {STEPS[currentStep].label}
            </span>
            <span className="text-xs text-muted-foreground">
              {currentStep + 1}/{STEPS.length}
            </span>
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto scrollbar-thin">
            <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto animate-fade-in" key={currentStep}>
              {stepComponents[currentStep]}
            </div>
          </div>

          {/* Fixed Bottom Navigation */}
          <div className="shrink-0 flex items-center justify-between border-t border-border bg-surface-raised px-4 sm:px-6 lg:px-8 py-4">
            <Button
              variant="outline"
              onClick={goBack}
              disabled={isFirst || saveStep.isPending}
            >
              <ChevronLeft className="h-4 w-4" />
              <span className="hidden sm:inline">Zurueck</span>
            </Button>

            <div className="hidden md:flex items-center gap-1.5">
              {STEPS.map((_, idx) => {
                const status = getValidationStatusForStep(idx);
                return (
                  <button
                    key={idx}
                    onClick={() => goToStep(idx)}
                    className={cn(
                      "w-2 h-2 rounded-full transition-all duration-200",
                      idx === currentStep && "bg-primary w-4",
                      idx !== currentStep && status === 'complete' && "bg-success",
                      idx !== currentStep && status === 'warning' && "bg-warning",
                      idx !== currentStep && status === 'error' && "bg-destructive",
                      idx !== currentStep && status === 'pending' && "bg-border"
                    )}
                    title={
                      status === 'complete' ? 'Vollstaendig' :
                      status === 'warning' ? 'Teilweise ausgefuellt' :
                      status === 'error' ? 'Pflichtfelder fehlen' :
                      'Noch nicht besucht'
                    }
                  />
                );
              })}
            </div>

            {!isLast && (
              <Button onClick={goNext} disabled={saveStep.isPending}>
                {saveStep.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <span className="hidden sm:inline">Weiter</span>
                    <ChevronRight className="h-4 w-4" />
                  </>
                )}
              </Button>
            )}

            {isLast && (
              <Button variant="outline" onClick={() => router.push("/streams")}>
                Zur Uebersicht
              </Button>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

/* ------------------------------------------------------------------ */
/* Exported page with Suspense boundary for useSearchParams            */
/* ------------------------------------------------------------------ */

export default function WizardPage() {
  return <WizardInner />;
}
