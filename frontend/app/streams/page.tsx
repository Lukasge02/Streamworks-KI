"use client";

import { useState, useRef, Suspense, useEffect } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { format } from "date-fns";
import { de } from "date-fns/locale";
import { motion, AnimatePresence } from "framer-motion";
import {
  Plus,
  Download,
  FileCode,
  Calendar,
  Tag,
  RefreshCw,
  Sparkles,
  Edit,
  Trash2,
  Clock,
  CheckCircle,
  Copy,
  Upload,
  Command,
  Search,
  Send,
  AlertCircle,
  Lightbulb,
} from "lucide-react";
import AppLayout from "../components/AppLayout";
import { Button } from "../components/ui/button";
import { cn } from "@/lib/utils";
import {
  useSessions,
  useDeleteSession,
  useDuplicateSession,
  useExecuteCommand,
  useImportSession,
  useSearchSessions,
  type Session,
} from "../../lib/api/streams";

function StreamsPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // TanStack Query hooks
  const { data: sessions = [], isLoading, refetch } = useSessions();
  const deleteMutation = useDeleteSession();
  const duplicateMutation = useDuplicateSession();
  const commandMutation = useExecuteCommand();
  const importMutation = useImportSession();

  // Local UI state
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [commandInput, setCommandInput] = useState("");
  const [commandResult, setCommandResult] = useState<{
    success: boolean;
    message: string;
    suggestions?: string[];
  } | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const commandInputRef = useRef<HTMLInputElement>(null);

  // Debounced search
  const { data: searchSuggestions = [] } = useSearchSessions(searchQuery);

  // Handle action from URL params
  useEffect(() => {
    const action = searchParams.get("action");
    const id = searchParams.get("id");
    if (action === "duplicate" && id) {
      duplicateMutation.mutate(id);
      router.replace("/streams");
    }
  }, [searchParams, router, duplicateMutation]);

  // Command execution handler
  const handleCommand = async () => {
    if (!commandInput.trim() || commandMutation.isPending) return;

    setCommandResult(null);
    setShowSuggestions(false);

    commandMutation.mutate(commandInput, {
      onSuccess: (data) => {
        if (data.success && data.redirect_url) {
          setCommandResult({ success: true, message: data.message });
          setTimeout(() => {
            router.push(data.redirect_url!);
          }, 500);
        } else if (data.success) {
          setCommandResult({ success: true, message: data.message });
          setCommandInput("");
        } else {
          setCommandResult({
            success: false,
            message: data.message,
            suggestions: data.suggestions,
          });
        }
      },
      onError: () => {
        setCommandResult({
          success: false,
          message: "Fehler bei der Befehlsausführung",
        });
      },
    });
  };

  // Search input handler with debounce
  const handleCommandInputChange = (value: string) => {
    setCommandInput(value);
    setCommandResult(null);
    setSearchQuery(value);
    setShowSuggestions(value.length >= 2);
  };

  // Quick action shortcuts
  const handleQuickAction = (action: string, session: Session) => {
    switch (action) {
      case "open":
        router.push(`/streams/${session.id}`);
        break;
      case "rename":
        setCommandInput(`Benenne "${session.name}" in "" um`);
        setShowSuggestions(false);
        commandInputRef.current?.focus();
        setTimeout(() => {
          const input = commandInputRef.current;
          if (input) {
            const pos = input.value.lastIndexOf('""') + 1;
            input.setSelectionRange(pos, pos);
          }
        }, 50);
        break;
      case "duplicate":
        duplicateMutation.mutate(session.id);
        break;
    }
  };

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id, {
      onSuccess: () => setDeleteId(null),
      onError: () => setDeleteId(null),
    });
  };

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    importMutation.mutate(file);

    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleEdit = (session: Session) => {
    if (session.status === "draft") {
      router.push(`/editor?session=${session.id}`);
    } else {
      router.push(`/streams/${session.id}`);
    }
  };

  const getJobTypeStyles = (jobType: string) => {
    switch (jobType) {
      case "FILE_TRANSFER":
        return "bg-purple-100 text-purple-700 border-purple-200";
      case "SAP":
        return "bg-orange-100 text-orange-700 border-orange-200";
      case "STANDARD":
        return "bg-emerald-100 text-emerald-700 border-emerald-200";
      default:
        return "bg-gray-100 text-gray-700 border-gray-200";
    }
  };

  const getStatusBadge = (status: string, completionPercent: number) => {
    if (status === "complete") {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-lg bg-emerald-100 text-emerald-700 border border-emerald-200">
          <CheckCircle className="w-3 h-3" />
          Fertig
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-lg bg-amber-100 text-amber-700 border border-amber-200">
        <Clock className="w-3 h-3" />
        Entwurf ({Math.round(completionPercent)}%)
      </span>
    );
  };

  return (
    <AppLayout>
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".xml"
        className="hidden"
      />

      {/* Top Bar */}
      <div className="flex items-center justify-between mb-6 flex-shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Meine Streams</h1>
          <p className="text-gray-500 text-sm mt-1">
            Entwürfe und fertige Streams verwalten
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleImportClick}
            isLoading={importMutation.isPending}
            className="gap-2"
          >
            <Upload className="w-4 h-4" />
            Import XML
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            isLoading={isLoading}
            className="gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Aktualisieren
          </Button>
          <Link href="/editor">
            <Button className="gap-2 bg-[#0082D9] hover:bg-[#0077C8]">
              <Plus className="w-4 h-4" />
              Neuer Stream
            </Button>
          </Link>
        </div>
      </div>

      {/* Command Input Bar */}
      <div className="mb-4 flex-shrink-0">
        <div className="relative">
          <div className="flex items-center gap-2 bg-gradient-to-r from-slate-50 to-blue-50 border border-slate-200 rounded-xl p-1 shadow-sm">
            <div className="flex items-center gap-2 px-3 text-slate-400 flex-shrink-0">
              <Command className="w-4 h-4" />
            </div>
            <input
              ref={commandInputRef}
              type="text"
              value={commandInput}
              onChange={(e) => handleCommandInputChange(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleCommand();
                }
                if (e.key === "Escape") {
                  setShowSuggestions(false);
                  setCommandResult(null);
                }
              }}
              onFocus={() =>
                searchSuggestions.length > 0 && setShowSuggestions(true)
              }
              placeholder='Was möchten Sie tun? z.B. "Benenne test123 in neuername um" oder "Öffne Stream xyz"'
              className="flex-1 bg-transparent border-none outline-none focus:ring-0 text-sm text-slate-700 placeholder:text-slate-400 py-2.5"
            />
            <Button
              size="sm"
              onClick={handleCommand}
              disabled={!commandInput.trim() || commandMutation.isPending}
              isLoading={commandMutation.isPending}
              className="gap-1.5 bg-[#0082D9] hover:bg-[#0077C8] rounded-lg mr-1"
            >
              {!commandMutation.isPending && <Send className="w-4 h-4" />}
              Ausführen
            </Button>
          </div>

          {/* Search Suggestions Dropdown */}
          <AnimatePresence>
            {showSuggestions && searchSuggestions.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-lg z-50 overflow-hidden"
              >
                <div className="p-2 border-b border-slate-100 bg-slate-50">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                    <Search className="w-3 h-3" />
                    Passende Streams
                  </span>
                </div>
                <div className="max-h-48 overflow-y-auto">
                  {searchSuggestions.map((s) => (
                    <div
                      key={s.id}
                      className="flex items-center justify-between px-3 py-2 hover:bg-blue-50 transition-colors group"
                    >
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <FileCode
                          className={cn(
                            "w-4 h-4 flex-shrink-0",
                            s.status === "complete"
                              ? "text-emerald-500"
                              : "text-amber-500"
                          )}
                        />
                        <span className="text-sm font-medium text-slate-700 truncate">
                          {s.name}
                        </span>
                        <span
                          className={cn(
                            "text-[10px] px-1.5 py-0.5 rounded font-medium",
                            s.status === "complete"
                              ? "bg-emerald-100 text-emerald-600"
                              : "bg-amber-100 text-amber-600"
                          )}
                        >
                          {s.job_type}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => handleQuickAction("open", s)}
                          className="px-2 py-1 text-xs text-blue-600 hover:bg-blue-100 rounded transition-colors"
                        >
                          Öffnen
                        </button>
                        <button
                          onClick={() => handleQuickAction("rename", s)}
                          className="px-2 py-1 text-xs text-slate-600 hover:bg-slate-100 rounded transition-colors"
                        >
                          Umbenennen
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Command Result */}
          <AnimatePresence>
            {commandResult && (
              <motion.div
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -5 }}
                className={cn(
                  "mt-2 p-3 rounded-lg border text-sm flex items-start gap-2",
                  commandResult.success
                    ? "bg-emerald-50 border-emerald-200 text-emerald-700"
                    : "bg-amber-50 border-amber-200 text-amber-700"
                )}
              >
                {commandResult.success ? (
                  <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                ) : (
                  <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <p>{commandResult.message}</p>
                  {commandResult.suggestions &&
                    commandResult.suggestions.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        <span className="text-xs text-slate-500 flex items-center gap-1">
                          <Lightbulb className="w-3 h-3" />
                          Beispiele:
                        </span>
                        {commandResult.suggestions.map((s, i) => (
                          <button
                            key={i}
                            onClick={() => setCommandInput(s)}
                            className="text-xs px-2 py-0.5 bg-white border border-amber-200 rounded hover:bg-amber-100 transition-colors"
                          >
                            {s}
                          </button>
                        ))}
                      </div>
                    )}
                </div>
                <button
                  onClick={() => setCommandResult(null)}
                  className="text-current opacity-50 hover:opacity-100 transition-opacity"
                >
                  ×
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Content Card */}
      <div className="flex-1 bg-white rounded-2xl shadow-soft border border-gray-100 overflow-hidden flex flex-col min-h-0">
        {isLoading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="w-10 h-10 border-4 border-gray-200 border-t-[#0082D9] rounded-full animate-spin" />
          </div>
        ) : sessions.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center p-12">
            <div className="w-20 h-20 bg-gray-100 rounded-2xl flex items-center justify-center mb-6">
              <FileCode className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Keine Streams gefunden
            </h3>
            <p className="text-gray-500 text-center max-w-sm mb-6">
              Erstellen Sie Ihren ersten Stream mit dem Editor oder importieren
              Sie eine XML-Datei.
            </p>
            <div className="flex gap-4">
              <Button
                variant="outline"
                onClick={handleImportClick}
                className="gap-2"
              >
                <Upload className="w-4 h-4" />
                XML Import
              </Button>
              <Link href="/editor">
                <Button className="gap-2 bg-[#0082D9] hover:bg-[#0077C8]">
                  <Sparkles className="w-4 h-4" />
                  Stream erstellen
                </Button>
              </Link>
            </div>
          </div>
        ) : (
          <div className="overflow-y-auto flex-1">
            <table className="w-full">
              <thead className="bg-gray-50/80 sticky top-0 z-10">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Stream
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Typ
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Zuletzt bearbeitet
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Aktionen
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                <AnimatePresence>
                  {sessions.map((session, index) => (
                    <motion.tr
                      key={session.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="hover:bg-gray-50/50 transition-colors group"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-4">
                          <div
                            className={cn(
                              "w-10 h-10 rounded-xl flex items-center justify-center",
                              session.status === "complete"
                                ? "bg-gradient-to-br from-emerald-100 to-emerald-200"
                                : "bg-gradient-to-br from-amber-100 to-amber-200"
                            )}
                          >
                            <FileCode
                              className={cn(
                                "w-5 h-5",
                                session.status === "complete"
                                  ? "text-emerald-600"
                                  : "text-amber-600"
                              )}
                            />
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">
                              {session.name || "Unbenannter Stream"}
                            </div>
                            <div className="text-xs text-gray-400 font-mono">
                              {session.id.substring(0, 8)}...
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {getStatusBadge(
                          session.status,
                          session.completion_percent
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={cn(
                            "inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-lg border",
                            getJobTypeStyles(session.job_type)
                          )}
                        >
                          <Tag className="w-3 h-3" />
                          {session.job_type}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2 text-gray-600">
                          <Calendar className="w-4 h-4 text-gray-400" />
                          <span className="text-sm">
                            {session.updated_at
                              ? format(
                                new Date(session.updated_at),
                                "dd. MMM yyyy, HH:mm",
                                { locale: de }
                              )
                              : "-"}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          {/* Duplicate Button */}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => duplicateMutation.mutate(session.id)}
                            title="Duplizieren"
                            className="text-gray-400 hover:text-blue-600 hover:bg-blue-50"
                          >
                            <Copy className="w-4 h-4" />
                          </Button>

                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEdit(session)}
                            className="gap-2 text-[#0082D9] hover:text-[#006BB3] hover:bg-[#0082D9]/5"
                          >
                            <Edit className="w-4 h-4" />
                            {session.status === "draft"
                              ? "Fortsetzen"
                              : "Bearbeiten"}
                          </Button>
                          {session.status === "complete" && (
                            <a
                              href={`http://localhost:8000/api/xml/download/${session.id}`}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                            >
                              <Download className="w-4 h-4" />
                            </a>
                          )}
                          {deleteId === session.id ? (
                            <div className="flex items-center gap-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDelete(session.id)}
                                isLoading={deleteMutation.isPending}
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              >
                                Ja
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setDeleteId(null)}
                                className="text-gray-600"
                              >
                                Nein
                              </Button>
                            </div>
                          ) : (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setDeleteId(session.id)}
                              className="text-gray-400 hover:text-red-600 hover:bg-red-50"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </AnimatePresence>
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Stats Footer */}
      {sessions.length > 0 && (
        <div className="mt-4 flex items-center justify-between text-sm text-gray-500 flex-shrink-0">
          <span>
            {sessions.filter((s) => s.status === "complete").length} fertig,{" "}
            {sessions.filter((s) => s.status === "draft").length} Entwürfe
          </span>
          <span>
            Zuletzt aktualisiert: {format(new Date(), "HH:mm", { locale: de })}{" "}
            Uhr
          </span>
        </div>
      )}
    </AppLayout>
  );
}

export default function StreamsPage() {
  return (
    <Suspense
      fallback={
        <AppLayout>
          <div className="flex-1 flex items-center justify-center">
            <div className="w-10 h-10 border-4 border-gray-200 border-t-[#0082D9] rounded-full animate-spin" />
          </div>
        </AppLayout>
      }
    >
      <StreamsPageContent />
    </Suspense>
  );
}
