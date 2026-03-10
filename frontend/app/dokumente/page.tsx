"use client";

import React, { useState, useRef } from "react";
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
  FolderPlus,
  Upload,
  Loader2,
  FileText,
  FileSpreadsheet,
  File,
  Search,
  Trash2,
  Eye,
  FolderInput,
  Folder,
  FolderOpen,
  ChevronRight,
  ChevronDown,
  Calendar,
} from "lucide-react";

import {
  useDocuments,
  useUploadDocument,
  useDeleteDocument,
} from "@/lib/api/chat";
import {
  useFolders,
  useCreateFolder,
  useUpdateFolder,
  useDeleteFolder,
  useMoveDocument,
} from "@/lib/api/documents";
import type { Folder as FolderType } from "@/lib/api/documents";

import DropZone from "./components/DropZone";
import CreateFolderDialog from "./components/CreateFolderDialog";
import MoveDocumentDialog from "./components/MoveDocumentDialog";
import DocumentPreviewDialog from "./components/DocumentPreviewDialog";

/* ------------------------------------------------------------------ */
/* Helper                                                              */
/* ------------------------------------------------------------------ */

function getFileIcon(mime: string) {
  if (mime.includes("pdf")) return FileText;
  if (mime.includes("spreadsheet") || mime.includes("csv"))
    return FileSpreadsheet;
  return File;
}

function mimeLabel(mime: string): string {
  if (mime.includes("pdf")) return "PDF";
  if (mime.includes("wordprocessingml")) return "DOCX";
  if (mime.includes("spreadsheetml")) return "XLSX";
  if (mime.includes("text/plain")) return "TXT";
  if (mime.includes("text/csv")) return "CSV";
  return mime.split("/").pop()?.toUpperCase() ?? "";
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("de-DE", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/* ------------------------------------------------------------------ */
/* Folder sidebar tree                                                 */
/* ------------------------------------------------------------------ */

function FolderSidebar({
  folders,
  activeFolderId,
  onSelectFolder,
  onCreateFolder,
  totalDocs,
}: {
  folders: FolderType[];
  activeFolderId: string | null;
  onSelectFolder: (id: string | null) => void;
  onCreateFolder: () => void;
  totalDocs: number;
}) {
  const [expanded, setExpanded] = useState<Set<string>>(
    () => new Set(folders.map((f) => f.id))
  );

  return (
    <aside className="hidden md:flex w-56 shrink-0 flex-col border-r bg-muted/30">
      <div className="flex items-center justify-between px-3 py-3 border-b">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Ordner
        </h2>
        <button
          type="button"
          onClick={onCreateFolder}
          className="rounded-md p-1 text-muted-foreground hover:text-accent hover:bg-accent/10 transition-colors"
          title="Neuer Ordner"
        >
          <FolderPlus className="h-3.5 w-3.5" />
        </button>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
        {/* All documents */}
        <button
          type="button"
          className={`flex w-full items-center gap-1.5 rounded-md px-2 py-1.5 text-sm transition-colors ${
            activeFolderId === null
              ? "bg-accent/15 text-accent font-medium"
              : "text-muted-foreground hover:bg-muted hover:text-foreground"
          }`}
          onClick={() => onSelectFolder(null)}
        >
          <FolderOpen className="h-4 w-4 shrink-0" />
          <span className="truncate">Alle Dokumente</span>
          <Badge variant="secondary" className="ml-auto text-[10px] px-1.5 py-0">
            {totalDocs}
          </Badge>
        </button>

        {/* User-created folders */}
        {folders.map((folder) => (
          <button
            key={folder.id}
            type="button"
            className={`flex w-full items-center gap-1.5 rounded-md px-2 py-1.5 text-sm transition-colors ${
              activeFolderId === folder.id
                ? "bg-accent/15 text-accent font-medium"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            }`}
            onClick={() => onSelectFolder(folder.id)}
          >
            <span
              className="h-3 w-3 rounded shrink-0"
              style={{ backgroundColor: folder.color }}
            />
            <Folder className="h-4 w-4 shrink-0" />
            <span className="truncate">{folder.name}</span>
            <Badge variant="secondary" className="ml-auto text-[10px] px-1.5 py-0">
              {folder.document_count}
            </Badge>
          </button>
        ))}

        {folders.length === 0 && (
          <p className="px-2 py-4 text-xs text-muted-foreground text-center">
            Noch keine Ordner erstellt
          </p>
        )}
      </div>
      <div className="border-t px-3 py-2">
        <p className="text-[10px] text-muted-foreground">
          {totalDocs} Dokument{totalDocs !== 1 ? "e" : ""} in {folders.length} Ordner{folders.length !== 1 ? "n" : ""}
        </p>
      </div>
    </aside>
  );
}

/* ------------------------------------------------------------------ */
/* Page                                                                */
/* ------------------------------------------------------------------ */

export default function DokumentePage() {
  const toast = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // State
  const [activeFolderId, setActiveFolderId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [createFolderOpen, setCreateFolderOpen] = useState(false);
  const [previewDocId, setPreviewDocId] = useState<string | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [moveDoc, setMoveDoc] = useState<{
    id: string;
    filename: string;
    folderId: string | null;
  } | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{
    id: string;
    filename: string;
  } | null>(null);

  // Rename/color edit state
  const [editFolder, setEditFolder] = useState<{
    id: string;
    name: string;
    color: string;
    mode: "rename" | "color";
  } | null>(null);

  // Data
  const { data: documents = [], isLoading: docsLoading } = useDocuments();
  const { data: folders = [], isLoading: foldersLoading } = useFolders();

  // Mutations
  const uploadDoc = useUploadDocument();
  const deleteDoc = useDeleteDocument();
  const createFolder = useCreateFolder();
  const updateFolder = useUpdateFolder();
  const deleteFolder = useDeleteFolder();
  const moveDocument = useMoveDocument();

  // Filter documents
  const filteredDocs = documents.filter((doc) => {
    const d = doc as typeof doc & { folder_id?: string | null };
    const matchesFolder =
      activeFolderId === null || d.folder_id === activeFolderId;
    const matchesSearch =
      !searchQuery ||
      doc.filename.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFolder && matchesSearch;
  });

  // Handlers
  function handleUploadFiles(files: File[]) {
    for (const file of files) {
      uploadDoc.mutate(
        { file, folderId: activeFolderId },
        {
          onSuccess: (data) =>
            toast.success(
              `"${data.filename}" hochgeladen (${data.chunks} Chunks)`
            ),
          onError: (err) => toast.error(err.message),
        }
      );
    }
  }

  function handleFileInput(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files?.length) return;
    handleUploadFiles(Array.from(files));
    e.target.value = "";
  }

  function handleCreateFolder(name: string, color: string) {
    createFolder.mutate(
      { name, color },
      {
        onSuccess: () => {
          toast.success(`Ordner "${name}" erstellt`);
          setCreateFolderOpen(false);
        },
        onError: (err) => toast.error(err.message),
      }
    );
  }

  function handleDeleteFolder(folderId: string) {
    const folder = folders.find((f) => f.id === folderId);
    deleteFolder.mutate(folderId, {
      onSuccess: () => {
        toast.success(
          `Ordner "${folder?.name}" geloescht. Dokumente ins Stammverzeichnis verschoben.`
        );
        if (activeFolderId === folderId) {
          setActiveFolderId(null);
        }
      },
      onError: (err) => toast.error(err.message),
    });
  }

  function handleMoveDocument(folderId: string | null) {
    if (!moveDoc) return;
    moveDocument.mutate(
      { documentId: moveDoc.id, folderId },
      {
        onSuccess: () => {
          toast.success("Dokument verschoben");
          setMoveDoc(null);
        },
        onError: (err) => toast.error(err.message),
      }
    );
  }

  function handleDeleteDocument() {
    if (!deleteConfirm) return;
    deleteDoc.mutate(deleteConfirm.id, {
      onSuccess: () => {
        toast.success("Dokument geloescht");
        setDeleteConfirm(null);
      },
      onError: (err) => toast.error(err.message),
    });
  }

  function handleRenameFolder(folder: { id: string; name: string; color: string }) {
    setEditFolder({ ...folder, mode: "rename" });
  }

  function handleChangeColor(folder: { id: string; name: string; color: string }) {
    setEditFolder({ ...folder, mode: "color" });
  }

  function handleSaveEdit() {
    if (!editFolder) return;
    const updates: { id: string; name?: string; color?: string } = {
      id: editFolder.id,
    };
    if (editFolder.mode === "rename") updates.name = editFolder.name;
    if (editFolder.mode === "color") updates.color = editFolder.color;

    updateFolder.mutate(updates, {
      onSuccess: () => {
        toast.success("Ordner aktualisiert");
        setEditFolder(null);
      },
      onError: (err) => toast.error(err.message),
    });
  }

  const PRESET_COLORS = [
    "#0066cc",
    "#059669",
    "#d97706",
    "#dc2626",
    "#7c3aed",
    "#db2777",
  ];

  const isLoading = docsLoading || foldersLoading;

  return (
    <AppLayout fullWidth noScroll>
      <DropZone onDrop={handleUploadFiles} disabled={uploadDoc.isPending}>
        <div className="flex h-full">
          {/* Sidebar */}
          <FolderSidebar
            folders={folders}
            activeFolderId={activeFolderId}
            onSelectFolder={setActiveFolderId}
            onCreateFolder={() => setCreateFolderOpen(true)}
            totalDocs={documents.length}
          />

          {/* Main content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header row */}
            <div className="flex items-center justify-between px-4 sm:px-6 py-4 border-b bg-background">
              <div>
                <h1 className="text-lg font-semibold text-primary">
                  Dokumentenverwaltung
                </h1>
                <p className="text-xs text-muted-foreground">
                  {documents.length} Dokument{documents.length !== 1 ? "e" : ""}{" "}
                  in {folders.length} Ordner{folders.length !== 1 ? "n" : ""}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx,.xlsx,.txt,.csv"
                  multiple
                  onChange={handleFileInput}
                  className="hidden"
                />
                <Button
                  size="sm"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploadDoc.isPending}
                >
                  {uploadDoc.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Upload className="h-4 w-4" />
                  )}
                  {uploadDoc.isPending ? "Hochladen..." : "Hochladen"}
                </Button>
              </div>
            </div>

            {/* Search bar */}
            <div className="px-4 sm:px-6 py-3 border-b bg-muted/20">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Dokumente suchen..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex h-9 w-full rounded-md border border-input bg-background pl-10 pr-4 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                />
              </div>
            </div>

            {/* Content area */}
            <div className="flex-1 overflow-y-auto">
              {/* Loading */}
              {isLoading && (
                <div className="flex items-center justify-center py-24">
                  <Loader2 className="h-8 w-8 animate-spin text-accent" />
                </div>
              )}

              {/* Empty state */}
              {!isLoading && filteredDocs.length === 0 && (
                <div className="flex flex-col items-center justify-center py-24 text-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted shadow-soft mb-4">
                    <FileText className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <h3 className="text-primary mb-1">
                    {searchQuery
                      ? "Keine Treffer"
                      : activeFolderId
                        ? "Ordner ist leer"
                        : "Noch keine Dokumente"}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-6 max-w-sm">
                    {searchQuery
                      ? "Versuche einen anderen Suchbegriff."
                      : "Ziehe Dateien hierher oder klicke auf Hochladen."}
                  </p>
                </div>
              )}

              {/* Document list */}
              {!isLoading && filteredDocs.length > 0 && (
                <div className="divide-y">
                  {/* Table header */}
                  <div className="grid grid-cols-[1fr_80px_80px_80px_140px_80px] gap-2 px-4 sm:px-6 py-2 text-xs font-medium text-muted-foreground uppercase tracking-wider bg-muted/30">
                    <span>Dateiname</span>
                    <span>Typ</span>
                    <span>Groesse</span>
                    <span>Chunks</span>
                    <span>Hochgeladen</span>
                    <span className="text-right">Aktionen</span>
                  </div>

                  {filteredDocs.map((doc) => {
                    const d = doc as typeof doc & { folder_id?: string | null };
                    const Icon = getFileIcon(doc.mime_type);
                    const folder = folders.find((f) => f.id === d.folder_id);

                    return (
                      <div
                        key={doc.id}
                        className="grid grid-cols-[1fr_80px_80px_80px_140px_80px] gap-2 px-4 sm:px-6 py-3 items-center hover:bg-muted/30 transition-colors group"
                      >
                        {/* Filename + folder */}
                        <div className="flex items-center gap-2.5 min-w-0">
                          <div className="shrink-0 rounded-lg bg-accent/10 p-1.5">
                            <Icon className="h-4 w-4 text-accent" />
                          </div>
                          <div className="min-w-0">
                            <p className="text-sm font-medium truncate">{doc.filename}</p>
                            {folder && (
                              <div className="flex items-center gap-1 mt-0.5">
                                <span
                                  className="h-2 w-2 rounded-full shrink-0"
                                  style={{ backgroundColor: folder.color }}
                                />
                                <span className="text-xs text-muted-foreground truncate">
                                  {folder.name}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Type */}
                        <div>
                          <Badge variant="secondary" className="text-[10px]">
                            {mimeLabel(doc.mime_type)}
                          </Badge>
                        </div>

                        {/* Size */}
                        <div className="text-xs text-muted-foreground">
                          {formatFileSize(doc.file_size)}
                        </div>

                        {/* Chunks */}
                        <div className="text-xs text-muted-foreground">
                          {doc.chunks}
                        </div>

                        {/* Date */}
                        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                          <Calendar className="h-3 w-3 shrink-0" />
                          <span>{doc.created_at ? formatDate(doc.created_at) : ""}</span>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center justify-end gap-0.5">
                          <button
                            onClick={() => {
                              setPreviewDocId(doc.id);
                              setPreviewOpen(true);
                            }}
                            className="h-7 w-7 flex items-center justify-center rounded-md opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-accent hover:bg-accent/10"
                            title="Vorschau"
                          >
                            <Eye className="h-3.5 w-3.5" />
                          </button>
                          <button
                            onClick={() =>
                              setMoveDoc({
                                id: doc.id,
                                filename: doc.filename,
                                folderId: d.folder_id ?? null,
                              })
                            }
                            className="h-7 w-7 flex items-center justify-center rounded-md opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-accent hover:bg-accent/10"
                            title="Verschieben"
                          >
                            <FolderInput className="h-3.5 w-3.5" />
                          </button>
                          <button
                            onClick={() =>
                              setDeleteConfirm({
                                id: doc.id,
                                filename: doc.filename,
                              })
                            }
                            disabled={deleteDoc.isPending && deleteDoc.variables === doc.id}
                            className="h-7 w-7 flex items-center justify-center rounded-md opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-destructive hover:bg-destructive/10 disabled:opacity-30"
                            title="Loeschen"
                          >
                            {deleteDoc.isPending && deleteDoc.variables === doc.id ? (
                              <Loader2 className="h-3.5 w-3.5 animate-spin" />
                            ) : (
                              <Trash2 className="h-3.5 w-3.5" />
                            )}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </DropZone>

      {/* Dialogs */}
      <CreateFolderDialog
        open={createFolderOpen}
        onOpenChange={setCreateFolderOpen}
        onSubmit={handleCreateFolder}
        isPending={createFolder.isPending}
      />

      <MoveDocumentDialog
        open={!!moveDoc}
        onOpenChange={(open) => !open && setMoveDoc(null)}
        folders={folders}
        currentFolderId={moveDoc?.folderId ?? null}
        documentName={moveDoc?.filename ?? ""}
        onMove={handleMoveDocument}
        isPending={moveDocument.isPending}
      />

      <DocumentPreviewDialog
        open={previewOpen}
        onOpenChange={setPreviewOpen}
        documentId={previewDocId}
      />

      {/* Delete confirmation */}
      <Dialog
        open={!!deleteConfirm}
        onOpenChange={(open) => !open && setDeleteConfirm(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Dokument loeschen?</DialogTitle>
            <DialogDescription>
              &quot;{deleteConfirm?.filename}&quot; wird unwiderruflich
              geloescht. Die zugehoerigen Chunks werden aus der Vektordatenbank
              entfernt.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteConfirm(null)}
            >
              Abbrechen
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteDocument}
              disabled={deleteDoc.isPending}
            >
              {deleteDoc.isPending ? "Loescht..." : "Endgueltig loeschen"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Rename / Color dialog */}
      <Dialog
        open={!!editFolder}
        onOpenChange={(open) => !open && setEditFolder(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editFolder?.mode === "rename"
                ? "Ordner umbenennen"
                : "Ordnerfarbe aendern"}
            </DialogTitle>
          </DialogHeader>

          {editFolder?.mode === "rename" && (
            <div>
              <label
                htmlFor="edit-folder-name"
                className="mb-1.5 block text-sm font-medium text-primary"
              >
                Neuer Name
              </label>
              <input
                id="edit-folder-name"
                type="text"
                value={editFolder.name}
                onChange={(e) =>
                  setEditFolder({ ...editFolder, name: e.target.value })
                }
                className="w-full rounded-md border border-border bg-surface-raised px-3 py-2 text-sm text-primary focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2"
                autoFocus
              />
            </div>
          )}

          {editFolder?.mode === "color" && (
            <div>
              <label className="mb-1.5 block text-sm font-medium text-primary">
                Farbe waehlen
              </label>
              <div className="flex gap-2">
                {PRESET_COLORS.map((c) => (
                  <button
                    key={c}
                    type="button"
                    onClick={() =>
                      setEditFolder({ ...editFolder, color: c })
                    }
                    className={`h-8 w-8 rounded-full border-2 transition-all ${
                      editFolder.color === c
                        ? "border-primary scale-110 shadow-md"
                        : "border-transparent hover:scale-105"
                    }`}
                    style={{ backgroundColor: c }}
                  />
                ))}
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setEditFolder(null)}>
              Abbrechen
            </Button>
            <Button
              onClick={handleSaveEdit}
              disabled={updateFolder.isPending}
            >
              {updateFolder.isPending ? "Speichert..." : "Speichern"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppLayout>
  );
}
