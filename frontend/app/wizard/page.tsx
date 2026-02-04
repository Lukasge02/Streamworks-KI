"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useState, useEffect, useCallback, Suspense } from "react";
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
/* Step Indicator                                                      */
/* ------------------------------------------------------------------ */

function StepIndicator({
  currentStep,
  onStepClick,
}: {
  currentStep: number;
  onStepClick: (step: number) => void;
}) {
  return (
    <nav className="mb-8">
      <ol className="flex items-center gap-1">
        {STEPS.map((step, idx) => {
          const Icon = step.icon;
          const isActive = idx === currentStep;
          const isComplete = idx < currentStep;

          return (
            <li key={idx} className="flex items-center flex-1 last:flex-none">
              <button
                type="button"
                onClick={() => onStepClick(idx)}
                className={cn(
                  "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
                  isActive &&
                    "bg-primary text-primary-foreground shadow-sm",
                  isComplete &&
                    !isActive &&
                    "bg-success-light text-success hover:bg-success-light/80",
                  !isActive &&
                    !isComplete &&
                    "text-muted-foreground hover:bg-muted hover:text-primary"
                )}
              >
                <span
                  className={cn(
                    "flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold shrink-0",
                    isActive && "bg-white/20",
                    isComplete && !isActive && "bg-success/10",
                    !isActive && !isComplete && "bg-muted"
                  )}
                >
                  {isComplete && !isActive ? (
                    <Check className="h-3.5 w-3.5" />
                  ) : (
                    idx
                  )}
                </span>
                <span className="hidden lg:inline">{step.label}</span>
              </button>
              {idx < STEPS.length - 1 && (
                <div
                  className={cn(
                    "mx-1 h-px flex-1 min-w-[12px]",
                    idx < currentStep ? "bg-success" : "bg-border"
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

  // Hydrate step data from session when loaded
  useEffect(() => {
    if (session?.data) {
      const hydrated: Record<number, Record<string, any>> = {};
      for (let i = 0; i <= 6; i++) {
        const key = `step_${i}`;
        if (session.data[key]) {
          hydrated[i] = session.data[key];
        }
      }
      setStepData((prev) => {
        // Only set if we haven't already populated to avoid overwriting user edits
        const hasData = Object.keys(prev).length > 0;
        return hasData ? prev : hydrated;
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
      setCurrentStep((s) => Math.min(s + 1, STEPS.length - 1));
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
    setCurrentStep((s) => Math.max(s - 1, 0));
  }

  async function goToStep(step: number) {
    if (step === currentStep) return;
    try {
      await saveCurrentStep();
    } catch {
      // continue navigation
    }
    setCurrentStep(step);
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

  /* ---- Resolve job type for step 4 ---- */
  const jobType =
    stepData[3]?.job_type ||
    session?.data?.step_3?.job_type ||
    session?.data?.job_type ||
    "STANDARD";

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
            if (params.schedule) step5Updates.schedule_frequency = params.schedule;
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
      />
    ),
  };

  const isFirst = currentStep === 0;
  const isLast = currentStep === STEPS.length - 1;

  return (
    <AppLayout>
      <div className="mb-6">
        <h1 className="text-primary">Stream-Wizard</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Erstellen Sie Schritt fuer Schritt einen neuen Automatisierungs-Stream
        </p>
      </div>

      <StepIndicator currentStep={currentStep} onStepClick={goToStep} />

      {/* Step Content */}
      <div className="min-h-[400px] animate-fade-in" key={currentStep}>
        {stepComponents[currentStep]}
      </div>

      {/* Navigation */}
      <div className="mt-8 flex items-center justify-between border-t border-border pt-6">
        <Button
          variant="outline"
          onClick={goBack}
          disabled={isFirst || saveStep.isPending}
        >
          <ChevronLeft className="h-4 w-4" />
          Zurueck
        </Button>

        <span className="text-sm text-muted-foreground">
          Schritt {currentStep + 1} von {STEPS.length}
        </span>

        {!isLast && (
          <Button onClick={goNext} disabled={saveStep.isPending}>
            {saveStep.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <>
                Weiter
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
    </AppLayout>
  );
}

/* ------------------------------------------------------------------ */
/* Exported page with Suspense boundary for useSearchParams            */
/* ------------------------------------------------------------------ */

export default function WizardPage() {
  return (
    <Suspense
      fallback={
        <AppLayout>
          <div className="flex items-center justify-center py-24">
            <Loader2 className="h-8 w-8 animate-spin text-accent" />
          </div>
        </AppLayout>
      }
    >
      <WizardInner />
    </Suspense>
  );
}
