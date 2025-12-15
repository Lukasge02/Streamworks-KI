"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Shield, Users, Check, AlertCircle, Save, Lock } from "lucide-react";
import { Button } from "./ui/button";
import DocumentAccessBadge, { AccessLevel } from "./DocumentAccessBadge";
import { cn } from "@/app/utils/cn";

interface DocumentAccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  docId: string;
  filename: string;
  currentLevel: AccessLevel;
  onSave: (
    docId: string,
    level: AccessLevel,
    allowedRoles: string[],
    allowedUsers: string[],
  ) => Promise<void>;
}

export default function DocumentAccessModal({
  isOpen,
  onClose,
  docId,
  filename,
  currentLevel,
  onSave,
}: DocumentAccessModalProps) {
  const [selectedLevel, setSelectedLevel] = useState<AccessLevel>(currentLevel);
  const [allowedRoles, setAllowedRoles] = useState<string[]>([]);
  const [allowedUsers, setAllowedUsers] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  // Reset state when opening
  useEffect(() => {
    if (isOpen) {
      setSelectedLevel(currentLevel);
      // In a real app, we would fetch existing specific permissions here
      setAllowedRoles([]);
      setAllowedUsers([]);
    }
  }, [isOpen, currentLevel, docId]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSave(docId, selectedLevel, allowedRoles, allowedUsers);
      onClose();
    } catch (error) {
      console.error("Failed to save permissions:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const levels: { id: AccessLevel; label: string; description: string }[] = [
    {
      id: "public",
      label: "Öffentlich",
      description: "Jeder kann dieses Dokument sehen.",
    },
    {
      id: "internal",
      label: "Intern",
      description: "Nur angemeldete Mitarbeiter (Standard).",
    },
    {
      id: "restricted",
      label: "Eingeschränkt",
      description: "Nur spezifische Rollen oder Benutzer.",
    },
    {
      id: "project",
      label: "Projekt",
      description: "Nur Mitglieder des verknüpften Projekts.",
    },
  ];

  const roles = ["admin", "manager", "developer", "viewer"];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-lg bg-white rounded-2xl shadow-xl z-50 overflow-hidden border border-gray-100"
          >
            <div className="flex items-center justify-between p-4 border-b border-gray-100">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Zugriffsrechte verwalten
                </h3>
                <p className="text-sm text-gray-500 truncate max-w-xs">
                  {filename}
                </p>
              </div>
              <Button variant="ghost" size="sm" onClick={onClose}>
                <X className="w-5 h-5 text-gray-500" />
              </Button>
            </div>

            <div className="p-6 space-y-6">
              {/* Access Level Selection */}
              <div className="space-y-3">
                <label className="text-sm font-medium text-gray-700">
                  Sichtbarkeit
                </label>
                <div className="grid grid-cols-1 gap-2">
                  {levels.map((level) => (
                    <div
                      key={level.id}
                      onClick={() => setSelectedLevel(level.id)}
                      className={cn(
                        "flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all",
                        selectedLevel === level.id
                          ? "bg-blue-50 border-blue-200 ring-1 ring-blue-200"
                          : "hover:bg-gray-50 border-gray-200",
                      )}
                    >
                      <div className="mt-0.5">
                        <div
                          className={cn(
                            "w-4 h-4 rounded-full border flex items-center justify-center",
                            selectedLevel === level.id
                              ? "border-blue-500 bg-blue-500"
                              : "border-gray-300",
                          )}
                        >
                          {selectedLevel === level.id && (
                            <Check className="w-3 h-3 text-white" />
                          )}
                        </div>
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-sm text-gray-900">
                            {level.label}
                          </span>
                          <DocumentAccessBadge
                            level={level.id}
                            showLabel={false}
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">
                          {level.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Role Selection (Only if restricted) */}
              {selectedLevel === "restricted" && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  className="space-y-3 pt-2 border-t border-gray-100"
                >
                  <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    Erlaubte Rollen
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {roles.map((role) => (
                      <button
                        key={role}
                        onClick={() => {
                          setAllowedRoles((prev) =>
                            prev.includes(role)
                              ? prev.filter((r) => r !== role)
                              : [...prev, role],
                          );
                        }}
                        className={cn(
                          "px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors",
                          allowedRoles.includes(role)
                            ? "bg-blue-100 text-blue-700 border-blue-200"
                            : "bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100",
                        )}
                      >
                        {role}
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-amber-600 flex items-center gap-1.5 bg-amber-50 p-2 rounded-lg">
                    <AlertCircle className="w-3 h-3" />
                    Benutzer müssen mindestens eine dieser Rollen haben.
                  </p>
                </motion.div>
              )}
            </div>

            <div className="p-4 bg-gray-50 border-t border-gray-100 flex items-center justify-end gap-3">
              <Button variant="ghost" onClick={onClose} disabled={isSaving}>
                Abbrechen
              </Button>
              <Button
                onClick={handleSave}
                disabled={isSaving}
                className="bg-[#0082D9] hover:bg-[#0077C8] text-white gap-2"
              >
                {isSaving ? "Speichert..." : "Speichern"}
                {!isSaving && <Save className="w-4 h-4" />}
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
