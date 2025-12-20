"use client";

import React, { useCallback, useState } from "react";
import { Upload, FileSpreadsheet, FileText, X, Loader2 } from "lucide-react";

interface FileUploadZoneProps {
    accept?: Record<string, string[]>;
    onFileSelect: (file: File) => void;
    isLoading?: boolean;
    maxSizeMB?: number;
    disabled?: boolean;
}

const DEFAULT_ACCEPT = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
        ".xlsx",
    ],
    "application/vnd.ms-excel": [".xls"],
    "text/csv": [".csv"],
    "application/pdf": [".pdf"],
};

const FILE_ICONS: Record<string, React.ReactNode> = {
    xlsx: <FileSpreadsheet className="w-8 h-8 text-emerald-500" />,
    xls: <FileSpreadsheet className="w-8 h-8 text-emerald-500" />,
    csv: <FileSpreadsheet className="w-8 h-8 text-blue-500" />,
    pdf: <FileText className="w-8 h-8 text-red-500" />,
};

export function FileUploadZone({
    accept = DEFAULT_ACCEPT,
    onFileSelect,
    isLoading = false,
    maxSizeMB = 10,
    disabled = false,
}: FileUploadZoneProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (!disabled) setIsDragging(true);
    }, [disabled]);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    }, []);

    const validateFile = useCallback(
        (file: File): boolean => {
            // Check size
            if (file.size > maxSizeMB * 1024 * 1024) {
                setError(`Datei zu groß (max. ${maxSizeMB} MB)`);
                return false;
            }

            // Check extension
            const ext = file.name.split(".").pop()?.toLowerCase();
            const validExts = Object.values(accept)
                .flat()
                .map((e) => e.replace(".", ""));

            if (!ext || !validExts.includes(ext)) {
                setError(`Ungültiger Dateityp. Erlaubt: ${validExts.join(", ")}`);
                return false;
            }

            setError(null);
            return true;
        },
        [accept, maxSizeMB]
    );

    const handleDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDragging(false);

            if (disabled) return;

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (validateFile(file)) {
                    setSelectedFile(file);
                    onFileSelect(file);
                }
            }
        },
        [disabled, validateFile, onFileSelect]
    );

    const handleFileInput = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            const files = e.target.files;
            if (files && files.length > 0) {
                const file = files[0];
                if (validateFile(file)) {
                    setSelectedFile(file);
                    onFileSelect(file);
                }
            }
            // Reset input
            e.target.value = "";
        },
        [validateFile, onFileSelect]
    );

    const clearFile = useCallback(() => {
        setSelectedFile(null);
        setError(null);
    }, []);

    const getFileIcon = (filename: string) => {
        const ext = filename.split(".").pop()?.toLowerCase() || "";
        return FILE_ICONS[ext] || <FileText className="w-8 h-8 text-gray-400" />;
    };

    const acceptString = Object.values(accept).flat().join(",");

    return (
        <div className="w-full">
            {/* Drop Zone */}
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`
          relative border-2 border-dashed rounded-xl p-6 transition-all duration-200
          ${isDragging
                        ? "border-[#0082D9] bg-blue-50/50 scale-[1.01]"
                        : "border-gray-200 hover:border-gray-300"
                    }
          ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
          ${error ? "border-red-300 bg-red-50/30" : ""}
        `}
            >
                <input
                    type="file"
                    accept={acceptString}
                    onChange={handleFileInput}
                    disabled={disabled || isLoading}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                />

                {isLoading ? (
                    <div className="flex flex-col items-center gap-3 py-4">
                        <Loader2 className="w-10 h-10 text-[#0082D9] animate-spin" />
                        <span className="text-sm text-gray-600">
                            Extrahiere Parameter...
                        </span>
                    </div>
                ) : selectedFile ? (
                    <div className="flex items-center gap-4">
                        {getFileIcon(selectedFile.name)}
                        <div className="flex-1 min-w-0">
                            <p className="font-medium text-gray-900 truncate">
                                {selectedFile.name}
                            </p>
                            <p className="text-sm text-gray-500">
                                {(selectedFile.size / 1024).toFixed(1)} KB
                            </p>
                        </div>
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                clearFile();
                            }}
                            className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                            <X className="w-5 h-5 text-gray-400" />
                        </button>
                    </div>
                ) : (
                    <div className="flex flex-col items-center gap-3 py-4">
                        <div
                            className={`
              p-3 rounded-xl transition-colors
              ${isDragging ? "bg-blue-100" : "bg-gray-100"}
            `}
                        >
                            <Upload
                                className={`w-8 h-8 ${isDragging ? "text-[#0082D9]" : "text-gray-400"}`}
                            />
                        </div>
                        <div className="text-center">
                            <p className="font-medium text-gray-700">
                                {isDragging
                                    ? "Datei hier ablegen"
                                    : "Datei hierher ziehen oder klicken"}
                            </p>
                            <p className="text-sm text-gray-500 mt-1">
                                Excel (.xlsx, .xls), CSV oder PDF
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {/* Error Message */}
            {error && (
                <p className="mt-2 text-sm text-red-600 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
                    {error}
                </p>
            )}

            {/* Supported Formats */}
            <div className="mt-3 flex flex-wrap gap-2">
                <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-emerald-50 text-emerald-700 text-xs font-medium">
                    <FileSpreadsheet className="w-3.5 h-3.5" />
                    Excel
                </span>
                <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-blue-50 text-blue-700 text-xs font-medium">
                    <FileSpreadsheet className="w-3.5 h-3.5" />
                    CSV
                </span>
                <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-red-50 text-red-700 text-xs font-medium">
                    <FileText className="w-3.5 h-3.5" />
                    PDF
                </span>
            </div>
        </div>
    );
}
