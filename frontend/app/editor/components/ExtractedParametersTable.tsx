"use client";

import React, { useState, useCallback } from "react";
import {
    Check,
    AlertTriangle,
    ChevronDown,
    ChevronUp,
    Edit2,
    X,
    FileSpreadsheet,
} from "lucide-react";
import { Button } from "../../components/ui/button";

// Types matching backend response
interface ParameterSource {
    type: "cell" | "text" | "inferred";
    location: string;
    original_text?: string;
}

interface ParameterData {
    value: string | number | boolean;
    confidence: number;
    source?: ParameterSource;
    is_explicit: boolean;
}

interface ExtractedStream {
    stream_name: string | null;
    job_type: "STANDARD" | "FILE_TRANSFER" | "SAP";
    parameters: Record<string, ParameterData>;
    missing_required: string[];
    row_number?: number;
    overall_confidence: number;
    warnings: string[];
}

interface ExtractedParametersTableProps {
    streams: ExtractedStream[];
    onEdit: (
        streamIndex: number,
        paramKey: string,
        newValue: string
    ) => void;
    onSelectStreams: (indices: number[]) => void;
    selectedIndices?: number[];
    showConfidence?: boolean;
}

const PARAM_LABELS: Record<string, string> = {
    stream_name: "Stream-Name",
    short_description: "Beschreibung",
    source_agent: "Quell-Agent",
    target_agent: "Ziel-Agent",
    source_file_pattern: "Quelldatei",
    target_file_path: "Zielpfad",
    agent_detail: "Agent/Server",
    main_script: "Script",
    schedule: "Zeitplan",
    start_time: "Startzeit",
    sap_system: "SAP-System",
    sap_report: "SAP-Report",
    sap_client: "Mandant",
    stream_priority: "Priorität",
    stream_owner: "Besitzer",
};

const JOB_TYPE_COLORS = {
    FILE_TRANSFER: "bg-blue-100 text-blue-700",
    STANDARD: "bg-purple-100 text-purple-700",
    SAP: "bg-orange-100 text-orange-700",
};

function ConfidenceBadge({ confidence }: { confidence: number }) {
    const percent = Math.round(confidence * 100);

    let colorClass = "bg-red-100 text-red-700";
    let icon: React.ReactNode = <AlertTriangle className="w-3 h-3" />;

    if (confidence >= 0.8) {
        colorClass = "bg-emerald-100 text-emerald-700";
        icon = <Check className="w-3 h-3" />;
    } else if (confidence >= 0.5) {
        colorClass = "bg-amber-100 text-amber-700";
        icon = null;
    }

    return (
        <span
            className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium ${colorClass}`}
        >
            {icon}
            {percent}%
        </span>
    );
}

function EditableCell({
    value,
    confidence,
    source,
    isExplicit,
    onSave,
    showConfidence,
}: {
    value: string;
    confidence: number;
    source?: ParameterSource;
    isExplicit: boolean;
    onSave: (newValue: string) => void;
    showConfidence: boolean;
}) {
    const [isEditing, setIsEditing] = useState(false);
    const [editValue, setEditValue] = useState(value);

    const handleSave = () => {
        onSave(editValue);
        setIsEditing(false);
    };

    const handleCancel = () => {
        setEditValue(value);
        setIsEditing(false);
    };

    if (isEditing) {
        return (
            <div className="flex items-center gap-1">
                <input
                    type="text"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") handleSave();
                        if (e.key === "Escape") handleCancel();
                    }}
                    className="flex-1 px-2 py-1 text-sm border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                />
                <button
                    onClick={handleSave}
                    className="p-1 text-emerald-600 hover:bg-emerald-50 rounded"
                >
                    <Check className="w-4 h-4" />
                </button>
                <button
                    onClick={handleCancel}
                    className="p-1 text-gray-400 hover:bg-gray-100 rounded"
                >
                    <X className="w-4 h-4" />
                </button>
            </div>
        );
    }

    return (
        <div className="group flex items-center gap-2">
            <span
                className={`flex-1 ${!isExplicit ? "text-gray-500 italic" : ""}`}
                title={source?.location}
            >
                {value || "-"}
            </span>
            {showConfidence && <ConfidenceBadge confidence={confidence} />}
            <button
                onClick={() => setIsEditing(true)}
                className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-gray-600 transition-opacity"
            >
                <Edit2 className="w-3.5 h-3.5" />
            </button>
        </div>
    );
}

function StreamRow({
    stream,
    index,
    isSelected,
    isExpanded,
    onToggleSelect,
    onToggleExpand,
    onEdit,
    showConfidence,
}: {
    stream: ExtractedStream;
    index: number;
    isSelected: boolean;
    isExpanded: boolean;
    onToggleSelect: () => void;
    onToggleExpand: () => void;
    onEdit: (paramKey: string, newValue: string) => void;
    showConfidence: boolean;
}) {
    const hasWarnings = stream.warnings.length > 0 || stream.missing_required.length > 0;

    // Get display parameters (filter out internal ones)
    const displayParams = Object.entries(stream.parameters).filter(
        ([key]) => !key.startsWith("_") && key !== "job_type" && key !== "confidence"
    );

    return (
        <>
            {/* Main Row */}
            <tr
                className={`
          border-b transition-colors cursor-pointer
          ${isSelected ? "bg-blue-50" : "hover:bg-gray-50"}
          ${hasWarnings ? "border-l-2 border-l-amber-400" : ""}
        `}
            >
                {/* Checkbox */}
                <td className="px-3 py-3">
                    <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={onToggleSelect}
                        className="w-4 h-4 rounded border-gray-300 text-[#0082D9] focus:ring-[#0082D9]"
                    />
                </td>

                {/* Row Number */}
                <td className="px-3 py-3 text-sm text-gray-500">
                    {stream.row_number || index + 1}
                </td>

                {/* Stream Name */}
                <td className="px-3 py-3">
                    <div className="font-medium text-gray-900">
                        {stream.stream_name || (
                            <span className="text-gray-400 italic">Kein Name</span>
                        )}
                    </div>
                </td>

                {/* Job Type */}
                <td className="px-3 py-3">
                    <span
                        className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${JOB_TYPE_COLORS[stream.job_type]}`}
                    >
                        {stream.job_type}
                    </span>
                </td>

                {/* Confidence */}
                <td className="px-3 py-3">
                    <ConfidenceBadge confidence={stream.overall_confidence} />
                </td>

                {/* Status */}
                <td className="px-3 py-3">
                    {stream.missing_required.length > 0 ? (
                        <span className="inline-flex items-center gap-1 text-xs text-amber-600">
                            <AlertTriangle className="w-3.5 h-3.5" />
                            {stream.missing_required.length} fehlend
                        </span>
                    ) : (
                        <span className="inline-flex items-center gap-1 text-xs text-emerald-600">
                            <Check className="w-3.5 h-3.5" />
                            Vollständig
                        </span>
                    )}
                </td>

                {/* Expand */}
                <td className="px-3 py-3">
                    <button
                        onClick={onToggleExpand}
                        className="p-1 rounded hover:bg-gray-100 transition-colors"
                    >
                        {isExpanded ? (
                            <ChevronUp className="w-4 h-4 text-gray-500" />
                        ) : (
                            <ChevronDown className="w-4 h-4 text-gray-500" />
                        )}
                    </button>
                </td>
            </tr>

            {/* Expanded Parameters */}
            {isExpanded && (
                <tr className="bg-gray-50/50">
                    <td colSpan={7} className="px-6 py-4">
                        <div className="grid grid-cols-2 gap-4">
                            {displayParams.map(([key, param]) => (
                                <div key={key} className="flex flex-col gap-1">
                                    <label className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        {PARAM_LABELS[key] || key}
                                    </label>
                                    <EditableCell
                                        value={String(param.value)}
                                        confidence={param.confidence}
                                        source={param.source}
                                        isExplicit={param.is_explicit}
                                        onSave={(newValue) => onEdit(key, newValue)}
                                        showConfidence={showConfidence}
                                    />
                                </div>
                            ))}
                        </div>

                        {/* Warnings */}
                        {stream.warnings.length > 0 && (
                            <div className="mt-4 p-3 bg-amber-50 rounded-lg border border-amber-200">
                                <p className="text-xs font-medium text-amber-800 mb-1">
                                    Hinweise:
                                </p>
                                <ul className="text-xs text-amber-700 space-y-0.5">
                                    {stream.warnings.map((warning, i) => (
                                        <li key={i}>• {warning}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </td>
                </tr>
            )}
        </>
    );
}

export function ExtractedParametersTable({
    streams,
    onEdit,
    onSelectStreams,
    selectedIndices = [],
    showConfidence = true,
}: ExtractedParametersTableProps) {
    const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

    const toggleSelect = useCallback(
        (index: number) => {
            const newSelected = selectedIndices.includes(index)
                ? selectedIndices.filter((i) => i !== index)
                : [...selectedIndices, index];
            onSelectStreams(newSelected);
        },
        [selectedIndices, onSelectStreams]
    );

    const toggleSelectAll = useCallback(() => {
        if (selectedIndices.length === streams.length) {
            onSelectStreams([]);
        } else {
            onSelectStreams(streams.map((_, i) => i));
        }
    }, [selectedIndices, streams, onSelectStreams]);

    const toggleExpand = useCallback((index: number) => {
        setExpandedRows((prev) => {
            const next = new Set(prev);
            if (next.has(index)) {
                next.delete(index);
            } else {
                next.add(index);
            }
            return next;
        });
    }, []);

    if (streams.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                <FileSpreadsheet className="w-12 h-12 mb-3 text-gray-300" />
                <p>Keine Streams extrahiert</p>
                <p className="text-sm text-gray-400 mt-1">
                    Laden Sie eine Datei hoch, um Parameter zu extrahieren
                </p>
            </div>
        );
    }

    return (
        <div className="w-full">
            {/* Summary Bar */}
            <div className="flex items-center justify-between mb-4 px-1">
                <div className="text-sm text-gray-600">
                    <span className="font-medium">{streams.length}</span> Stream(s)
                    extrahiert
                    {selectedIndices.length > 0 && (
                        <span className="ml-2 text-[#0082D9]">
                            ({selectedIndices.length} ausgewählt)
                        </span>
                    )}
                </div>
                <div className="flex items-center gap-3 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                        <span className="w-2 h-2 rounded-full bg-emerald-500" />
                        {"≥80% Konfidenz"}
                    </span>
                    <span className="flex items-center gap-1">
                        <span className="w-2 h-2 rounded-full bg-amber-400" />
                        50-79%
                    </span>
                    <span className="flex items-center gap-1">
                        <span className="w-2 h-2 rounded-full bg-red-400" />
                        {"<50%"}
                    </span>
                </div>
            </div>

            {/* Table */}
            <div className="border rounded-xl overflow-hidden bg-white shadow-sm">
                <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                        <tr>
                            <th className="px-3 py-3 text-left w-10">
                                <input
                                    type="checkbox"
                                    checked={
                                        selectedIndices.length === streams.length &&
                                        streams.length > 0
                                    }
                                    onChange={toggleSelectAll}
                                    className="w-4 h-4 rounded border-gray-300 text-[#0082D9] focus:ring-[#0082D9]"
                                />
                            </th>
                            <th className="px-3 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-12">
                                #
                            </th>
                            <th className="px-3 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                Stream-Name
                            </th>
                            <th className="px-3 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-32">
                                Job-Typ
                            </th>
                            <th className="px-3 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-24">
                                Konfidenz
                            </th>
                            <th className="px-3 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-28">
                                Status
                            </th>
                            <th className="px-3 py-3 w-10" />
                        </tr>
                    </thead>
                    <tbody>
                        {streams.map((stream, index) => (
                            <StreamRow
                                key={index}
                                stream={stream}
                                index={index}
                                isSelected={selectedIndices.includes(index)}
                                isExpanded={expandedRows.has(index)}
                                onToggleSelect={() => toggleSelect(index)}
                                onToggleExpand={() => toggleExpand(index)}
                                onEdit={(paramKey, newValue) => onEdit(index, paramKey, newValue)}
                                showConfidence={showConfidence}
                            />
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Create Sessions Button */}
            {selectedIndices.length > 0 && (
                <div className="mt-4 flex justify-end">
                    <Button className="gap-2">
                        <FileSpreadsheet className="w-4 h-4" />
                        {selectedIndices.length} Stream(s) erstellen
                    </Button>
                </div>
            )}
        </div>
    );
}
