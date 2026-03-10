"use client";

import React, { useState } from "react";
import {
  FolderOpen,
  MoreHorizontal,
  Pencil,
  Palette,
  Trash2,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { Folder } from "@/lib/api/documents";

interface FolderBarProps {
  folders: Folder[];
  activeFolderId: string | null;
  onSelectFolder: (folderId: string | null) => void;
  onRenameFolder: (folder: Folder) => void;
  onChangeColor: (folder: Folder) => void;
  onDeleteFolder: (folderId: string) => void;
}

function FolderChip({
  folder,
  isActive,
  onClick,
  onRename,
  onChangeColor,
  onDelete,
}: {
  folder: Folder;
  isActive: boolean;
  onClick: () => void;
  onRename: () => void;
  onChangeColor: () => void;
  onDelete: () => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={onClick}
        className={cn(
          "group flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium transition-all whitespace-nowrap",
          isActive
            ? "bg-accent/10 text-accent shadow-sm"
            : "bg-muted/50 text-muted-foreground hover:bg-muted hover:text-primary"
        )}
      >
        <span
          className="h-2.5 w-2.5 rounded-full shrink-0"
          style={{ backgroundColor: folder.color }}
        />
        <span>{folder.name}</span>
        <Badge
          variant="secondary"
          className="text-[10px] px-1.5 py-0 ml-0.5"
        >
          {folder.document_count}
        </Badge>
        <button
          onClick={(e) => {
            e.stopPropagation();
            setMenuOpen(!menuOpen);
          }}
          className="ml-0.5 rounded-sm p-0.5 opacity-0 group-hover:opacity-60 hover:!opacity-100 transition-opacity"
        >
          <MoreHorizontal className="h-3.5 w-3.5" />
        </button>
      </button>

      {/* Dropdown menu */}
      {menuOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setMenuOpen(false)}
          />
          <div className="absolute top-full left-0 z-50 mt-1 w-44 rounded-md border border-border bg-surface-raised py-1 shadow-elevated">
            <button
              className="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-primary hover:bg-muted transition-colors"
              onClick={() => {
                setMenuOpen(false);
                onRename();
              }}
            >
              <Pencil className="h-3.5 w-3.5" />
              Umbenennen
            </button>
            <button
              className="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-primary hover:bg-muted transition-colors"
              onClick={() => {
                setMenuOpen(false);
                onChangeColor();
              }}
            >
              <Palette className="h-3.5 w-3.5" />
              Farbe aendern
            </button>
            <div className="mx-2 my-1 border-t border-border" />
            <button
              className="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-destructive hover:bg-destructive/5 transition-colors"
              onClick={() => {
                setMenuOpen(false);
                onDelete();
              }}
            >
              <Trash2 className="h-3.5 w-3.5" />
              Loeschen
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default function FolderBar({
  folders,
  activeFolderId,
  onSelectFolder,
  onRenameFolder,
  onChangeColor,
  onDeleteFolder,
}: FolderBarProps) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto scrollbar-thin pb-1">
      {/* "All documents" chip */}
      <button
        onClick={() => onSelectFolder(null)}
        className={cn(
          "flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium transition-all whitespace-nowrap",
          activeFolderId === null
            ? "bg-accent/10 text-accent shadow-sm"
            : "bg-muted/50 text-muted-foreground hover:bg-muted hover:text-primary"
        )}
      >
        <FolderOpen className="h-3.5 w-3.5" />
        Alle Dokumente
      </button>

      {folders.map((folder) => (
        <FolderChip
          key={folder.id}
          folder={folder}
          isActive={activeFolderId === folder.id}
          onClick={() => onSelectFolder(folder.id)}
          onRename={() => onRenameFolder(folder)}
          onChangeColor={() => onChangeColor(folder)}
          onDelete={() => onDeleteFolder(folder.id)}
        />
      ))}
    </div>
  );
}
