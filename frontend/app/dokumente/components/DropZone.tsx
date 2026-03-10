"use client";

import React, { useState, useCallback } from "react";
import { Upload } from "lucide-react";
import { cn } from "@/lib/utils";

interface DropZoneProps {
  onDrop: (files: File[]) => void;
  disabled?: boolean;
  children: React.ReactNode;
}

export default function DropZone({ onDrop, disabled, children }: DropZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const dragCounter = React.useRef(0);

  const handleDragEnter = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounter.current++;
      if (e.dataTransfer.items?.length) {
        setIsDragging(true);
      }
    },
    []
  );

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current--;
    if (dragCounter.current === 0) {
      setIsDragging(false);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);
      dragCounter.current = 0;

      if (disabled) return;

      const files = Array.from(e.dataTransfer.files);
      if (files.length > 0) {
        onDrop(files);
      }
    },
    [onDrop, disabled]
  );

  return (
    <div
      className="relative"
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      {children}

      {/* Drag overlay */}
      {isDragging && (
        <div
          className={cn(
            "absolute inset-0 z-50 flex flex-col items-center justify-center gap-3",
            "rounded-lg border-2 border-dashed border-accent bg-accent/5 backdrop-blur-sm",
            "pointer-events-none"
          )}
        >
          <div className="rounded-full bg-accent/10 p-4">
            <Upload className="h-8 w-8 text-accent" />
          </div>
          <p className="text-sm font-medium text-accent">
            Dateien hier ablegen
          </p>
          <p className="text-xs text-muted-foreground">
            PDF, DOCX, XLSX, TXT
          </p>
        </div>
      )}
    </div>
  );
}
