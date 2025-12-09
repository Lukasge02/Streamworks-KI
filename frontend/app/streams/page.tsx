"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { format } from "date-fns";
import { de } from "date-fns/locale";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Download, FileCode, Calendar, Tag, RefreshCw, Sparkles, Edit, Trash2, Clock, CheckCircle, Copy, Upload } from "lucide-react";
import AppLayout from "../components/AppLayout";
import { Button } from "../components/ui/button";
import { cn } from "../utils/cn";

interface SessionData {
    id: string;
    name: string;
    status: "draft" | "complete";
    job_type: string;
    current_step: string;
    completion_percent: number;
    created_at: string;
    updated_at: string;
    params: Record<string, unknown>;
}

export default function StreamsPage() {
    const [sessions, setSessions] = useState<SessionData[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [deleteId, setDeleteId] = useState<string | null>(null);
    const [isImporting, setIsImporting] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const router = useRouter();

    useEffect(() => {
        fetchSessions();
    }, []);

    const fetchSessions = async () => {
        setIsLoading(true);
        try {
            const res = await fetch("http://localhost:8000/api/wizard/sessions");
            if (res.ok) {
                const data = await res.json();
                setSessions(data);
            }
        } catch (error) {
            console.error("Error loading sessions:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = useCallback(async (id: string) => {
        try {
            const res = await fetch(`http://localhost:8000/api/wizard/sessions/${id}`, {
                method: "DELETE",
            });
            if (res.ok) {
                setSessions((prev) => prev.filter((s) => s.id !== id));
            }
        } catch (error) {
            console.error("Error deleting session:", error);
        } finally {
            setDeleteId(null);
        }
    }, []);

    const handleDuplicate = async (id: string) => {
        try {
            const res = await fetch(`http://localhost:8000/api/wizard/sessions/${id}/duplicate`, {
                method: "POST",
            });
            if (res.ok) {
                fetchSessions();
            }
        } catch (error) {
            console.error("Error duplicating session:", error);
        }
    };

    const handleImportClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setIsImporting(true);
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("http://localhost:8000/api/wizard/sessions/import", {
                method: "POST",
                body: formData,
            });

            if (res.ok) {
                const data = await res.json();
                // Optionally redirect to the imported session
                // router.push(`/editor?session=${data.session_id}`);
                fetchSessions(); // Or just refresh list
            } else {
                console.error("Import failed");
            }
        } catch (error) {
            console.error("Error importing file:", error);
        } finally {
            setIsImporting(false);
            if (fileInputRef.current) fileInputRef.current.value = ""; // Reset
        }
    };

    const handleEdit = (session: SessionData) => {
        if (session.status === "draft") {
            // Resume draft in wizard
            router.push(`/editor?session=${session.id}`);
        } else {
            // Open completed stream in detail view
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
                    <p className="text-gray-500 text-sm mt-1">Entwürfe und fertige Streams verwalten</p>
                </div>
                <div className="flex items-center gap-3">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleImportClick}
                        disabled={isImporting}
                        className="gap-2"
                    >
                        <Upload className={cn("w-4 h-4", isImporting && "animate-pulse")} />
                        Import XML
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={fetchSessions}
                        disabled={isLoading}
                        className="gap-2"
                    >
                        <RefreshCw className={cn("w-4 h-4", isLoading && "animate-spin")} />
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
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Keine Streams gefunden</h3>
                        <p className="text-gray-500 text-center max-w-sm mb-6">
                            Erstellen Sie Ihren ersten Stream mit dem Editor oder importieren Sie eine XML-Datei.
                        </p>
                        <div className="flex gap-4">
                            <Button variant="outline" onClick={handleImportClick} className="gap-2">
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
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Stream</th>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Typ</th>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Zuletzt bearbeitet</th>
                                    <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Aktionen</th>
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
                                                    <div className={cn(
                                                        "w-10 h-10 rounded-xl flex items-center justify-center",
                                                        session.status === "complete"
                                                            ? "bg-gradient-to-br from-emerald-100 to-emerald-200"
                                                            : "bg-gradient-to-br from-amber-100 to-amber-200"
                                                    )}>
                                                        <FileCode className={cn(
                                                            "w-5 h-5",
                                                            session.status === "complete" ? "text-emerald-600" : "text-amber-600"
                                                        )} />
                                                    </div>
                                                    <div>
                                                        <div className="font-medium text-gray-900">{session.name || "Unbenannter Stream"}</div>
                                                        <div className="text-xs text-gray-400 font-mono">
                                                            {session.id.substring(0, 8)}...
                                                        </div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                {getStatusBadge(session.status, session.completion_percent)}
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={cn(
                                                    "inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-lg border",
                                                    getJobTypeStyles(session.job_type)
                                                )}>
                                                    <Tag className="w-3 h-3" />
                                                    {session.job_type}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-2 text-gray-600">
                                                    <Calendar className="w-4 h-4 text-gray-400" />
                                                    <span className="text-sm">
                                                        {session.updated_at
                                                            ? format(new Date(session.updated_at), "dd. MMM yyyy, HH:mm", { locale: de })
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
                                                        onClick={() => handleDuplicate(session.id)}
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
                                                        {session.status === "draft" ? "Fortsetzen" : "Bearbeiten"}
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
                        {sessions.filter(s => s.status === "complete").length} fertig,{" "}
                        {sessions.filter(s => s.status === "draft").length} Entwürfe
                    </span>
                    <span>Zuletzt aktualisiert: {format(new Date(), "HH:mm", { locale: de })} Uhr</span>
                </div>
            )}
        </AppLayout>
    );
}
