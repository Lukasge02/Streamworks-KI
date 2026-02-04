"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import AppLayout from "@/components/AppLayout";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { useToast } from "@/components/ui/toast";
import {
  useWizardSessions,
  useCreateSession,
  useDeleteSession,
} from "@/lib/api/wizard";
import {
  Plus,
  Trash2,
  Calendar,
  Workflow,
  Loader2,
  FileCode2,
} from "lucide-react";

/* ------------------------------------------------------------------ */
/* Helper                                                              */
/* ------------------------------------------------------------------ */

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("de-DE", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function jobTypeBadgeVariant(
  jobType?: string
): "default" | "secondary" | "success" | "warning" {
  switch (jobType) {
    case "STANDARD":
      return "default";
    case "FILE_TRANSFER":
      return "success";
    case "SAP":
      return "warning";
    default:
      return "secondary";
  }
}

/* ------------------------------------------------------------------ */
/* Page                                                                */
/* ------------------------------------------------------------------ */

export default function StreamsPage() {
  const router = useRouter();
  const toast = useToast();

  const { data: sessions, isLoading } = useWizardSessions();
  const createSession = useCreateSession();
  const deleteSession = useDeleteSession();

  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  /* ---- Actions ---- */

  async function handleCreate() {
    try {
      const session = await createSession.mutateAsync();
      router.push(`/wizard?session=${session.id}`);
    } catch {
      toast.error("Sitzung konnte nicht erstellt werden.");
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    try {
      await deleteSession.mutateAsync(deleteTarget);
      toast.success("Stream-Sitzung geloescht.");
    } catch {
      toast.error("Loeschen fehlgeschlagen.");
    } finally {
      setDeleteTarget(null);
    }
  }

  /* ---- Render ---- */

  return (
    <AppLayout>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-primary">Stream-Uebersicht</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Verwalten Sie Ihre Streamworks-Automatisierungen
          </p>
        </div>
        <Button
          onClick={handleCreate}
          disabled={createSession.isPending}
          size="lg"
        >
          {createSession.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Plus className="h-4 w-4" />
          )}
          Neuer Stream
        </Button>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-24">
          <Loader2 className="h-8 w-8 animate-spin text-accent" />
        </div>
      )}

      {/* Empty State */}
      {!isLoading && (!sessions || sessions.length === 0) && (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted mb-4">
            <FileCode2 className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-primary mb-1">Keine Streams vorhanden</h3>
          <p className="text-sm text-muted-foreground mb-6 max-w-sm">
            Erstellen Sie Ihren ersten Streamworks-Automatisierungsstream mit
            dem KI-gestuetzten Wizard.
          </p>
          <Button onClick={handleCreate} disabled={createSession.isPending}>
            <Plus className="h-4 w-4" />
            Neuer Stream erstellen
          </Button>
        </div>
      )}

      {/* Session Grid */}
      {!isLoading && sessions && sessions.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {sessions.map((session) => {
            const name =
              session.data?.step_1?.stream_name ||
              session.data?.name ||
              "Unbenannter Stream";
            const jobType =
              session.data?.step_3?.job_type || session.data?.job_type;
            const description =
              session.data?.step_1?.short_description ||
              session.data?.description;

            return (
              <Card
                key={session.id}
                className="card-hover cursor-pointer group"
                onClick={() => router.push(`/wizard?session=${session.id}`)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <Workflow className="h-4 w-4 text-accent shrink-0" />
                      <CardTitle className="text-base line-clamp-2">
                        {name}
                      </CardTitle>
                    </div>
                    {jobType && (
                      <Badge variant={jobTypeBadgeVariant(jobType)}>
                        {jobType}
                      </Badge>
                    )}
                  </div>
                  {description && (
                    <CardDescription className="line-clamp-2 mt-1">
                      {description}
                    </CardDescription>
                  )}
                </CardHeader>

                <CardContent>
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Calendar className="h-3.5 w-3.5" />
                    <span>Erstellt: {formatDate(session.created_at)}</span>
                  </div>
                </CardContent>

                <CardFooter className="justify-end gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-accent"
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`/xml-editor?session=${session.id}`);
                    }}
                  >
                    <FileCode2 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-destructive"
                    onClick={(e) => {
                      e.stopPropagation();
                      setDeleteTarget(session.id);
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </CardFooter>
              </Card>
            );
          })}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Stream loeschen</DialogTitle>
            <DialogDescription>
              Sind Sie sicher, dass Sie diese Stream-Sitzung unwiderruflich
              loeschen moechten?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>
              Abbrechen
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteSession.isPending}
            >
              {deleteSession.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Trash2 className="h-4 w-4" />
              )}
              Loeschen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppLayout>
  );
}
