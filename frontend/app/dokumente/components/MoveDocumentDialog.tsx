"use client";

import React from "react";
import { FolderOpen, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import type { Folder } from "@/lib/api/documents";
import { cn } from "@/lib/utils";

interface MoveDocumentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  folders: Folder[];
  currentFolderId: string | null;
  documentName: string;
  onMove: (folderId: string | null) => void;
  isPending: boolean;
}

export default function MoveDocumentDialog({
  open,
  onOpenChange,
  folders,
  currentFolderId,
  documentName,
  onMove,
  isPending,
}: MoveDocumentDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Dokument verschieben</DialogTitle>
          <DialogDescription>
            Waehle einen Zielordner fuer &quot;{documentName}&quot;.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-1 py-2">
          {/* Root option */}
          <button
            onClick={() => onMove(null)}
            disabled={isPending || currentFolderId === null}
            className={cn(
              "flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors text-left",
              currentFolderId === null
                ? "bg-accent/10 text-accent cursor-default"
                : "hover:bg-muted text-primary"
            )}
          >
            <Home className="h-4 w-4 shrink-0" />
            <span className="font-medium">Stammverzeichnis</span>
            {currentFolderId === null && (
              <span className="ml-auto text-xs text-muted-foreground">
                Aktuell
              </span>
            )}
          </button>

          {/* Folders */}
          {folders.map((folder) => (
            <button
              key={folder.id}
              onClick={() => onMove(folder.id)}
              disabled={isPending || currentFolderId === folder.id}
              className={cn(
                "flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors text-left",
                currentFolderId === folder.id
                  ? "bg-accent/10 text-accent cursor-default"
                  : "hover:bg-muted text-primary"
              )}
            >
              <div
                className="h-4 w-4 rounded shrink-0 flex items-center justify-center"
                style={{ backgroundColor: folder.color + "20" }}
              >
                <FolderOpen
                  className="h-3 w-3"
                  style={{ color: folder.color }}
                />
              </div>
              <span className="font-medium">{folder.name}</span>
              {currentFolderId === folder.id && (
                <span className="ml-auto text-xs text-muted-foreground">
                  Aktuell
                </span>
              )}
            </button>
          ))}

          {folders.length === 0 && (
            <p className="px-3 py-4 text-sm text-muted-foreground text-center">
              Noch keine Ordner erstellt.
            </p>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Abbrechen
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
