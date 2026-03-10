"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

const PRESET_COLORS = [
  "#0066cc",
  "#059669",
  "#d97706",
  "#dc2626",
  "#7c3aed",
  "#db2777",
];

interface CreateFolderDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (name: string, color: string) => void;
  isPending: boolean;
}

export default function CreateFolderDialog({
  open,
  onOpenChange,
  onSubmit,
  isPending,
}: CreateFolderDialogProps) {
  const [name, setName] = useState("");
  const [color, setColor] = useState(PRESET_COLORS[0]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    onSubmit(name.trim(), color);
    setName("");
    setColor(PRESET_COLORS[0]);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Neuer Ordner</DialogTitle>
          <DialogDescription>
            Erstelle einen Ordner, um deine Dokumente zu organisieren.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="folder-name"
              className="mb-1.5 block text-sm font-medium text-primary"
            >
              Ordnername
            </label>
            <input
              id="folder-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="z.B. Anforderungen, SAP-Dokumente..."
              className="w-full rounded-md border border-border bg-surface-raised px-3 py-2 text-sm text-primary placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2"
              autoFocus
            />
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-primary">
              Farbe
            </label>
            <div className="flex gap-2">
              {PRESET_COLORS.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => setColor(c)}
                  className={cn(
                    "h-8 w-8 rounded-full border-2 transition-all",
                    color === c
                      ? "border-primary scale-110 shadow-md"
                      : "border-transparent hover:scale-105"
                  )}
                  style={{ backgroundColor: c }}
                  title={c}
                />
              ))}
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Abbrechen
            </Button>
            <Button type="submit" disabled={!name.trim() || isPending}>
              {isPending ? "Erstelle..." : "Ordner erstellen"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
