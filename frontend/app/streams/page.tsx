"use client";

import { useRouter } from "next/navigation";
import { useState, useRef, useMemo, useCallback, useEffect } from "react";
import AppLayout from "@/components/AppLayout";
import { Button } from "@/components/ui/button";
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
  useDeleteSession,
  useQuickEdit,
  useApplyQuickEdit,
  type QuickEditPreview,
} from "@/lib/api/wizard";
import {
  Plus,
  Trash2,
  Calendar,
  Workflow,
  Loader2,
  FileCode2,
  Wand2,
  Check,
  Sparkles,
  Folder,
  FolderOpen,
  ChevronRight,
  ChevronDown,
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
/* Folder structure                                                    */
/* ------------------------------------------------------------------ */

interface FolderNode {
  label: string;
  key: string;
  children?: FolderNode[];
}

const folderTree: FolderNode[] = [
  {
    label: "Alle Streams",
    key: "all",
  },
  {
    label: "Produktion",
    key: "produktion",
    children: [
      { label: "SAP-Jobs", key: "produktion/sap" },
      { label: "File-Transfers", key: "produktion/ft" },
      { label: "Standard-Jobs", key: "produktion/std" },
    ],
  },
  {
    label: "Entwicklung",
    key: "entwicklung",
    children: [
      { label: "Test-Streams", key: "entwicklung/test" },
      { label: "Prototypen", key: "entwicklung/proto" },
    ],
  },
  {
    label: "Archiv",
    key: "archiv",
  },
];

function FolderTree({
  nodes,
  activeKey,
  onSelect,
  depth = 0,
}: {
  nodes: FolderNode[];
  activeKey: string;
  onSelect: (key: string) => void;
  depth?: number;
}) {
  const [expanded, setExpanded] = useState<Set<string>>(
    () => new Set(["produktion", "entwicklung"])
  );

  return (
    <ul className="space-y-0.5">
      {nodes.map((node) => {
        const hasChildren = node.children && node.children.length > 0;
        const isExpanded = expanded.has(node.key);
        const isActive = activeKey === node.key;
        const FolderIcon = isExpanded && hasChildren ? FolderOpen : Folder;
        const ChevronIcon = isExpanded ? ChevronDown : ChevronRight;

        return (
          <li key={node.key}>
            <button
              type="button"
              className={`flex w-full items-center gap-1.5 rounded-md px-2 py-1.5 text-sm transition-colors ${
                isActive
                  ? "bg-accent/15 text-accent font-medium"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
              style={{ paddingLeft: `${depth * 12 + 8}px` }}
              onClick={() => {
                onSelect(node.key);
                if (hasChildren) {
                  setExpanded((prev) => {
                    const next = new Set(prev);
                    if (next.has(node.key)) next.delete(node.key);
                    else next.add(node.key);
                    return next;
                  });
                }
              }}
            >
              {hasChildren ? (
                <ChevronIcon className="h-3.5 w-3.5 shrink-0" />
              ) : (
                <span className="w-3.5" />
              )}
              <FolderIcon className="h-4 w-4 shrink-0" />
              <span className="truncate">{node.label}</span>
            </button>
            {hasChildren && isExpanded && (
              <FolderTree
                nodes={node.children!}
                activeKey={activeKey}
                onSelect={onSelect}
                depth={depth + 1}
              />
            )}
          </li>
        );
      })}
    </ul>
  );
}

/* ------------------------------------------------------------------ */
/* Page                                                                */
/* ------------------------------------------------------------------ */

export default function StreamsPage() {
  const router = useRouter();
  const toast = useToast();

  const { data: sessions, isLoading } = useWizardSessions();
  const deleteSession = useDeleteSession();

  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [activeFolder, setActiveFolder] = useState("all");

  /* ---- Quick Edit ---- */
  const [editInstruction, setEditInstruction] = useState("");
  const [editPreview, setEditPreview] = useState<QuickEditPreview | null>(null);
  const quickEdit = useQuickEdit();
  const applyQuickEdit = useApplyQuickEdit();
  const inputRef = useRef<HTMLInputElement>(null);

  // Autocomplete state
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [autocompleteIdx, setAutocompleteIdx] = useState(0);
  const [mentionStart, setMentionStart] = useState<number | null>(null);

  const streamNames = useMemo(() => {
    if (!sessions) return [];
    return sessions.map(
      (s) => s.data?.step_1?.stream_name || s.data?.name || "Unbenannter Stream"
    );
  }, [sessions]);

  // Filtered autocomplete suggestions based on text after @
  const autocompleteSuggestions = useMemo(() => {
    if (mentionStart === null) return [];
    const query = editInstruction.slice(mentionStart + 1).toLowerCase();
    return streamNames.filter((n) => n.toLowerCase().includes(query));
  }, [mentionStart, editInstruction, streamNames]);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = e.target.value;
      setEditInstruction(val);

      const cursor = e.target.selectionStart ?? val.length;
      const textBeforeCursor = val.slice(0, cursor);
      const atIdx = textBeforeCursor.lastIndexOf("@");

      if (atIdx !== -1) {
        const textAfterAt = textBeforeCursor.slice(atIdx + 1);
        if (!textAfterAt.includes(" ") || textAfterAt.length < 20) {
          setMentionStart(atIdx);
          setShowAutocomplete(true);
          setAutocompleteIdx(0);
          return;
        }
      }
      setShowAutocomplete(false);
      setMentionStart(null);
    },
    []
  );

  const insertMention = useCallback(
    (name: string) => {
      if (mentionStart === null) return;
      const before = editInstruction.slice(0, mentionStart);
      const after = editInstruction.slice(
        editInstruction.indexOf(" ", mentionStart + 1) === -1
          ? editInstruction.length
          : editInstruction.indexOf(" ", mentionStart + 1)
      );
      setEditInstruction(`${before}${name}${after}`);
      setShowAutocomplete(false);
      setMentionStart(null);
      inputRef.current?.focus();
    },
    [editInstruction, mentionStart]
  );

  const handleInputKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (showAutocomplete && autocompleteSuggestions.length > 0) {
        if (e.key === "ArrowDown") {
          e.preventDefault();
          setAutocompleteIdx((i) =>
            i < autocompleteSuggestions.length - 1 ? i + 1 : 0
          );
          return;
        }
        if (e.key === "ArrowUp") {
          e.preventDefault();
          setAutocompleteIdx((i) =>
            i > 0 ? i - 1 : autocompleteSuggestions.length - 1
          );
          return;
        }
        if (e.key === "Tab" || e.key === "Enter") {
          e.preventDefault();
          insertMention(autocompleteSuggestions[autocompleteIdx]);
          return;
        }
        if (e.key === "Escape") {
          e.preventDefault();
          setShowAutocomplete(false);
          return;
        }
      }
      if (e.key === "Enter") handleQuickEdit();
    },
    [showAutocomplete, autocompleteSuggestions, autocompleteIdx, insertMention]
  );

  useEffect(() => {
    if (!showAutocomplete) return;
    const handler = () => setShowAutocomplete(false);
    document.addEventListener("click", handler);
    return () => document.removeEventListener("click", handler);
  }, [showAutocomplete]);

  const exampleSuggestions = useMemo(() => {
    const first = streamNames[0];
    if (!first) return [];
    return [
      `Benenne ${first} um zu ${first}_V2`,
      `Setze die Email auf admin@firma.de in ${first}`,
      `Aendere die Prioritaet auf hoch`,
    ];
  }, [streamNames]);

  async function handleQuickEdit() {
    if (!editInstruction.trim() || !sessions?.length) return;

    const sessionNames: Record<string, string> = {};
    for (const s of sessions) {
      sessionNames[s.id] =
        s.data?.step_1?.stream_name || s.data?.name || "Unbenannter Stream";
    }

    try {
      const preview = await quickEdit.mutateAsync({
        instruction: editInstruction,
        session_names: sessionNames,
      });

      if (preview.error || !preview.changes.length) {
        toast.error(preview.message || "Keine Aenderungen erkannt.");
        return;
      }

      setEditPreview(preview);
    } catch {
      toast.error("KI-Analyse fehlgeschlagen.");
    }
  }

  async function handleApplyEdit() {
    if (!editPreview?.session_id || !editPreview.changes.length) return;

    try {
      await applyQuickEdit.mutateAsync({
        session_id: editPreview.session_id,
        changes: editPreview.changes,
      });
      toast.success(
        `Stream "${editPreview.session_name}" erfolgreich aktualisiert.`
      );
      setEditPreview(null);
      setEditInstruction("");
    } catch {
      toast.error("Aenderungen konnten nicht gespeichert werden.");
    }
  }

  /* ---- Actions ---- */

  function handleCreate() {
    router.push("/wizard");
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
    <AppLayout fullWidth noScroll>
      <div className="flex h-full">
        {/* Sidebar: Folder tree */}
        <aside className="hidden md:flex w-56 shrink-0 flex-col border-r bg-muted/30">
          <div className="px-3 py-3 border-b">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Ordner
            </h2>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            <FolderTree
              nodes={folderTree}
              activeKey={activeFolder}
              onSelect={setActiveFolder}
            />
          </div>
          <div className="border-t px-3 py-2">
            <p className="text-[10px] text-muted-foreground">
              {sessions?.length ?? 0} Stream{(sessions?.length ?? 0) !== 1 ? "s" : ""} gesamt
            </p>
          </div>
        </aside>

        {/* Main content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header row */}
          <div className="flex items-center justify-between px-4 sm:px-6 py-4 border-b bg-background">
            <div>
              <h1 className="text-lg font-semibold text-primary">Stream-Uebersicht</h1>
              <p className="text-xs text-muted-foreground">
                Verwalten Sie Ihre Streamworks-Automatisierungen
              </p>
            </div>
            <Button onClick={handleCreate} size="sm">
              <Plus className="h-4 w-4" />
              Neuer Stream
            </Button>
          </div>

          {/* Quick Edit Command Bar */}
          {!isLoading && sessions && sessions.length > 0 && (
            <div className="px-4 sm:px-6 py-3 border-b bg-muted/20 space-y-2">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Sparkles className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-accent" />
                  <input
                    ref={inputRef}
                    type="text"
                    className="flex h-9 w-full rounded-md border border-input bg-background px-10 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder="Stream per KI bearbeiten — tippe @ fuer Stream-Namen"
                    value={editInstruction}
                    onChange={handleInputChange}
                    onKeyDown={handleInputKeyDown}
                    disabled={quickEdit.isPending}
                  />
                  {showAutocomplete && autocompleteSuggestions.length > 0 && (
                    <div className="absolute left-0 top-full mt-1 z-50 w-full max-h-48 overflow-y-auto rounded-md border bg-popover shadow-md">
                      {autocompleteSuggestions.map((name, i) => (
                        <button
                          key={name}
                          type="button"
                          className={`flex w-full items-center gap-2 px-3 py-2 text-sm text-left hover:bg-accent/10 ${
                            i === autocompleteIdx ? "bg-accent/10" : ""
                          }`}
                          onMouseDown={(e) => {
                            e.preventDefault();
                            insertMention(name);
                          }}
                        >
                          <Workflow className="h-3.5 w-3.5 text-accent shrink-0" />
                          {name}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <Button
                  onClick={handleQuickEdit}
                  disabled={quickEdit.isPending || !editInstruction.trim()}
                  size="sm"
                >
                  {quickEdit.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Wand2 className="h-4 w-4" />
                  )}
                  Ausfuehren
                </Button>
              </div>
              {!editInstruction && exampleSuggestions.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  <span className="text-xs text-muted-foreground pt-0.5">Beispiele:</span>
                  {exampleSuggestions.map((ex) => (
                    <button
                      key={ex}
                      type="button"
                      className="inline-flex items-center rounded-full border border-border bg-muted/50 px-2.5 py-0.5 text-xs text-muted-foreground hover:bg-accent/10 hover:text-accent transition-colors"
                      onClick={() => {
                        setEditInstruction(ex);
                        inputRef.current?.focus();
                      }}
                    >
                      {ex}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Content area */}
          <div className="flex-1 overflow-y-auto">
            {/* Loading */}
            {isLoading && (
              <div className="flex items-center justify-center py-24">
                <Loader2 className="h-8 w-8 animate-spin text-accent" />
              </div>
            )}

            {/* Empty State */}
            {!isLoading && (!sessions || sessions.length === 0) && (
              <div className="flex flex-col items-center justify-center py-24 text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted shadow-soft mb-4">
                  <FileCode2 className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="text-primary mb-1">Keine Streams vorhanden</h3>
                <p className="text-sm text-muted-foreground mb-6 max-w-sm">
                  Erstellen Sie Ihren ersten Streamworks-Automatisierungsstream mit
                  dem KI-gestuetzten Wizard.
                </p>
                <Button onClick={handleCreate}>
                  <Plus className="h-4 w-4" />
                  Neuer Stream erstellen
                </Button>
              </div>
            )}

            {/* Stream List */}
            {!isLoading && sessions && sessions.length > 0 && (
              <div className="divide-y">
                {/* Table header */}
                <div className="grid grid-cols-[1fr_120px_140px_180px_80px] gap-2 px-4 sm:px-6 py-2 text-xs font-medium text-muted-foreground uppercase tracking-wider bg-muted/30">
                  <span>Stream-Name</span>
                  <span>Typ</span>
                  <span>Kontakt</span>
                  <span>Erstellt</span>
                  <span className="text-right">Aktionen</span>
                </div>

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
                  const contact =
                    session.data?.step_2?.contact_name || "";

                  return (
                    <div
                      key={session.id}
                      className="grid grid-cols-[1fr_120px_140px_180px_80px] gap-2 px-4 sm:px-6 py-3 items-center hover:bg-muted/30 cursor-pointer transition-colors group"
                      onClick={() => router.push(`/wizard?session=${session.id}`)}
                    >
                      {/* Name + Description */}
                      <div className="flex items-center gap-2.5 min-w-0">
                        <Workflow className="h-4 w-4 text-accent shrink-0" />
                        <div className="min-w-0">
                          <p className="text-sm font-medium truncate">{name}</p>
                          {description && (
                            <p className="text-xs text-muted-foreground truncate">
                              {description}
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Job Type */}
                      <div>
                        {jobType ? (
                          <Badge variant={jobTypeBadgeVariant(jobType)} className="text-[10px]">
                            {jobType}
                          </Badge>
                        ) : (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                      </div>

                      {/* Contact */}
                      <div className="truncate text-sm text-muted-foreground">
                        {contact || "—"}
                      </div>

                      {/* Date */}
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <Calendar className="h-3 w-3 shrink-0" />
                        <span>{formatDate(session.created_at)}</span>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center justify-end gap-0.5">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-accent"
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/xml-editor?session=${session.id}`);
                          }}
                        >
                          <FileCode2 className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-destructive"
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeleteTarget(session.id);
                          }}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Edit Confirmation Dialog */}
      <Dialog
        open={!!editPreview}
        onOpenChange={(open) => !open && setEditPreview(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Aenderungen bestaetigen</DialogTitle>
            <DialogDescription>
              {editPreview?.message}
            </DialogDescription>
          </DialogHeader>

          {editPreview?.session_name && (
            <p className="text-sm text-muted-foreground">
              Stream: <span className="font-medium text-foreground">{editPreview.session_name}</span>
            </p>
          )}

          {editPreview?.changes && editPreview.changes.length > 0 && (
            <div className="border rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-muted/50">
                    <th className="text-left px-3 py-2 font-medium">Feld</th>
                    <th className="text-left px-3 py-2 font-medium">Aktuell</th>
                    <th className="text-left px-3 py-2 font-medium">Neu</th>
                  </tr>
                </thead>
                <tbody>
                  {editPreview.changes.map((change, i) => (
                    <tr key={i} className="border-t">
                      <td className="px-3 py-2 text-muted-foreground">
                        {change.label}
                      </td>
                      <td className="px-3 py-2">
                        {change.old_value || (
                          <span className="text-muted-foreground italic">leer</span>
                        )}
                      </td>
                      <td className="px-3 py-2">
                        <span className="text-green-600 font-medium">
                          {change.new_value}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setEditPreview(null)}>
              Abbrechen
            </Button>
            <Button
              onClick={handleApplyEdit}
              disabled={applyQuickEdit.isPending}
            >
              {applyQuickEdit.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Check className="h-4 w-4" />
              )}
              Aenderungen uebernehmen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

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
