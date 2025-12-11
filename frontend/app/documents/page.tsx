"use client";

import { useState, useEffect, useCallback } from "react";

const API_URL = "http://localhost:8000";

interface Document {
    doc_id: string;
    filename: string;
    doc_type: string;
    content_preview?: string;
    created_at?: string;
    category?: string;
    parent_doc_id?: string;
}

interface Category {
    name: string;
    path: string;
    parent: string | null;
    document_count: number;
    children: Category[];
}

interface SearchResult {
    doc_id: string;
    content: string;
    filename: string;
    score: number;
    metadata: Record<string, unknown>;
}

interface DocumentDetail {
    doc_id: string;
    content: string;
    metadata: Record<string, unknown>;
    has_original?: boolean;
}

interface OriginalFile {
    filename: string;
    mime_type: string;
    data_url?: string;  // For base64 encoded files
    presigned_url?: string;  // For direct MinIO access
    size_bytes?: number;
    storage?: string;
}

interface UploadProgress {
    filename: string;
    status: "pending" | "uploading" | "success" | "error";
    phase: "waiting" | "uploading" | "storing" | "parsing" | "chunking" | "embedding" | "done";
    progress: number;
    error?: string;
}

// Processing phases configuration
const PROCESSING_PHASES = [
    { key: "uploading", label: "Upload", icon: "📤", description: "Datei hochladen" },
    { key: "storing", label: "Speichern", icon: "💾", description: "Original speichern" },
    { key: "parsing", label: "Parsing", icon: "📄", description: "Text extrahieren" },
    { key: "chunking", label: "Chunking", icon: "✂️", description: "In Abschnitte teilen" },
    { key: "embedding", label: "Embedding", icon: "🔗", description: "Vektoren erstellen" },
    { key: "done", label: "Fertig", icon: "✅", description: "Abgeschlossen" },
] as const;

interface DocumentChunk {
    doc_id: string;
    content: string;
    chunk_index: number;
    total_chunks: number;
}

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [stats, setStats] = useState<{ points_count: number } | null>(null);
    const [activeTab, setActiveTab] = useState<"list" | "search">("list");

    // Fullscreen Viewer State
    const [showViewer, setShowViewer] = useState(false);
    const [viewerDoc, setViewerDoc] = useState<DocumentDetail | null>(null);
    const [originalFile, setOriginalFile] = useState<OriginalFile | null>(null);
    const [chunks, setChunks] = useState<DocumentChunk[]>([]);
    const [loadingViewer, setLoadingViewer] = useState(false);

    // Upload Modal State
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [uploadQueue, setUploadQueue] = useState<UploadProgress[]>([]);
    const [isUploading, setIsUploading] = useState(false);
    const [dragActive, setDragActive] = useState(false);
    const [isUploadMinimized, setIsUploadMinimized] = useState(false);

    // Search state
    const [searchQuery, setSearchQuery] = useState("");
    const [debugInfo, setDebugInfo] = useState<{ parentId?: string; docId?: string; filename?: string; error?: string; details?: string } | null>(null);

    // Sync state
    const [isSyncing, setIsSyncing] = useState(false);
    const [syncResult, setSyncResult] = useState<{
        in_sync?: boolean;
        orphaned_qdrant_entries?: string[];
        orphaned_minio_files?: string[];
        qdrant_cleaned?: number;
        minio_cleaned?: number;
    } | null>(null);

    // Category state
    const [categories, setCategories] = useState<Category[]>([]);
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [showCategorySidebar, setShowCategorySidebar] = useState(true);

    // Category management state
    const [showCreateCategoryModal, setShowCreateCategoryModal] = useState(false);
    const [newCategoryName, setNewCategoryName] = useState("");
    const [editingCategory, setEditingCategory] = useState<string | null>(null);
    const [editCategoryName, setEditCategoryName] = useState("");
    const [categoryToDelete, setCategoryToDelete] = useState<string | null>(null);

    // Sync storage function
    const syncStorage = async () => {
        setIsSyncing(true);
        try {
            const res = await fetch(`${API_URL}/api/documents/sync`, { method: "POST" });
            const data = await res.json();
            console.log("Sync API response:", data);
            setSyncResult(data);
            loadDocuments(); // Reload after sync
            // Keep sync result to show green/amber status
        } catch (error) {
            console.error("Sync failed:", error);
            setSyncResult(null);
        } finally {
            setIsSyncing(false);
        }
    };

    // Load documents and stats
    const loadDocuments = useCallback(async () => {
        setIsLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/documents/list?limit=50`);
            const data = await res.json();
            setDocuments(data.documents || []);
            setStats({ points_count: data.total || 0 });
        } catch (error) {
            console.error("Failed to load documents:", error);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Load categories
    const loadCategories = useCallback(async () => {
        try {
            const res = await fetch(`${API_URL}/api/documents/categories`);
            const data = await res.json();
            setCategories(data.categories || []);
        } catch (error) {
            console.error("Failed to load categories:", error);
        }
    }, []);

    // Create new category
    const createCategory = async () => {
        if (!newCategoryName.trim()) return;
        try {
            const res = await fetch(`${API_URL}/api/documents/categories`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: newCategoryName.trim() })
            });
            if (res.ok) {
                setNewCategoryName("");
                setShowCreateCategoryModal(false);
                loadCategories();
            }
        } catch (error) {
            console.error("Failed to create category:", error);
        }
    };

    // Rename category
    const renameCategory = async (oldName: string, newName: string) => {
        if (!newName.trim()) return;
        try {
            const res = await fetch(`${API_URL}/api/documents/categories/${encodeURIComponent(oldName)}/rename`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ new_name: newName.trim() })
            });
            if (res.ok) {
                setEditingCategory(null);
                setEditCategoryName("");
                loadCategories();
                if (selectedCategory === oldName) {
                    setSelectedCategory(newName.trim());
                }
            }
        } catch (error) {
            console.error("Failed to rename category:", error);
        }
    };

    // Delete category
    const deleteCategory = async (categoryName: string) => {
        try {
            const res = await fetch(`${API_URL}/api/documents/categories/${encodeURIComponent(categoryName)}`, {
                method: "DELETE"
            });
            if (res.ok) {
                setCategoryToDelete(null);
                if (selectedCategory === categoryName) {
                    setSelectedCategory(null);
                }
                loadCategories();
                loadDocuments(); // Reload docs as they moved to Allgemein
            }
        } catch (error) {
            console.error("Failed to delete category:", error);
        }
    };

    useEffect(() => {
        syncStorage(); // Auto-sync on page load
        loadDocuments();
        loadCategories();
    }, [loadDocuments, loadCategories]);

    // Load chunk content on demand
    const loadChunkContent = async (chunkId: string): Promise<string> => {
        try {
            const res = await fetch(`${API_URL}/api/documents/${chunkId}`);
            if (res.ok) {
                const data = await res.json();
                return data.content || "";
            }
            return "Fehler beim Laden";
        } catch (e) {
            console.error("Failed to load chunk content:", e);
            return "Fehler beim Laden";
        }
    };

    // Open fullscreen viewer
    const openViewer = async (docId: string) => {
        setShowViewer(true);
        setLoadingViewer(true);
        setOriginalFile(null);
        setChunks([]);
        setViewerDoc(null);

        try {
            // Load document detail first
            const docRes = await fetch(`${API_URL}/api/documents/${docId}`);
            const docData = await docRes.json();
            setViewerDoc(docData);

            // Determine the correct ID for the original file
            // Priority: parent_doc_id > doc_id from response > original docId param
            const parentId = docData.metadata?.parent_doc_id || docData.doc_id || docId;
            const filename = docData.metadata?.filename;

            console.log("🔍 Looking for original file:", { parentId, docId, filename });
            setDebugInfo({ parentId, docId, filename });

            // Smart loading strategy: Try presigned URL first (better for large files)
            try {
                // Step 1: Try presigned URL (direct MinIO access, no memory issues)
                let presignedRes = await fetch(`${API_URL}/api/documents/${parentId}/presigned`);

                if (!presignedRes.ok && parentId !== docId) {
                    presignedRes = await fetch(`${API_URL}/api/documents/${docId}/presigned`);
                }

                if (presignedRes.ok) {
                    const presignedData = await presignedRes.json();

                    if (presignedData.url) {
                        // Use presigned URL - file loads directly from MinIO
                        console.log("✅ Using presigned URL:", presignedData.filename, `(${Math.round(presignedData.size_bytes / 1024)}KB)`);
                        setOriginalFile({
                            filename: presignedData.filename,
                            mime_type: presignedData.mime_type,
                            size_bytes: presignedData.size_bytes,
                            presigned_url: presignedData.url,
                            storage: "minio"
                        });
                    } else if (presignedData.size_bytes && presignedData.size_bytes < 2 * 1024 * 1024) {
                        // Small file, presigned not available - use base64
                        console.log("📦 Small file, using base64:", presignedData.filename);
                        const origRes = await fetch(`${API_URL}/api/documents/${parentId}/original`);
                        if (origRes.ok) {
                            const origData = await origRes.json();
                            setOriginalFile(origData);
                        }
                    } else {
                        // Large file but no presigned URL - show message
                        console.warn("⚠️ Large file without presigned URL");
                        setDebugInfo((prev) => ({ ...prev, error: "Large file - presigned URL not available" }));
                    }
                } else {
                    // Fallback: Try base64 endpoint (works for local storage)
                    console.log("📦 Fallback to base64 endpoint...");
                    let origRes = await fetch(`${API_URL}/api/documents/${parentId}/original`);

                    if (!origRes.ok && parentId !== docId) {
                        origRes = await fetch(`${API_URL}/api/documents/${docId}/original`);
                    }

                    if (origRes.ok) {
                        const origData = await origRes.json();
                        console.log("✅ Original file loaded (base64):", origData.filename);
                        setOriginalFile(origData);
                    } else {
                        const errorText = await origRes.text();
                        console.error("❌ Original file not found:", origRes.status, errorText);
                        setDebugInfo((prev) => ({ ...prev, error: `Status: ${origRes.status}`, details: errorText }));
                    }
                }
            } catch (e) {
                console.error("❌ Original file fetch error:", e);
                setDebugInfo((prev) => ({ ...prev, error: String(e) }));
            }

            // Load all chunks for this document
            try {
                const searchRes = await fetch(`${API_URL}/api/documents/list?limit=500`);
                if (searchRes.ok) {
                    const searchData = await searchRes.json();
                    const allDocs = searchData.documents || [];

                    // Filter to find all chunks belonging to this document
                    // Match by: same parent_doc_id OR same filename
                    const docChunks = allDocs
                        .filter((d: Document & { parent_doc_id?: string }) => {
                            return d.filename === filename || d.parent_doc_id === parentId;
                        })
                        // Sort by chunk_index from API (not doc_id!)
                        .sort((a: Document & { chunk_index?: number }, b: Document & { chunk_index?: number }) => {
                            const aIdx = a.chunk_index ?? 999;
                            const bIdx = b.chunk_index ?? 999;
                            return aIdx - bIdx;
                        })
                        .map((d: Document & { chunk_index?: number, total_chunks?: number }) => ({
                            doc_id: d.doc_id,
                            content: "", // Will be loaded on demand
                            chunk_index: d.chunk_index ?? 0,
                            total_chunks: d.total_chunks ?? 1
                        }));

                    console.log("📦 Found chunks:", docChunks.length, docChunks.map((c: { chunk_index: number }) => c.chunk_index));
                    setChunks(docChunks);
                }
            } catch (e) {
                console.log("Failed to load chunks:", e);
            }

        } catch (error) {
            console.error("Failed to load viewer:", error);
        } finally {
            setLoadingViewer(false);
        }
    };




    // Handle file selection
    const handleFileSelect = (files: FileList | null) => {
        if (!files || files.length === 0) return;

        const newFiles: UploadProgress[] = Array.from(files).map(file => ({
            filename: file.name,
            status: "pending" as const,
            phase: "waiting" as const,
            progress: 0
        }));

        setUploadQueue(prev => [...prev, ...newFiles]);
    };

    // Upload all files in queue with phase transitions
    const startUpload = async () => {
        if (uploadQueue.length === 0 || isUploading) return;

        setIsUploading(true);
        const fileInput = document.getElementById('panel-file-input') as HTMLInputElement;
        const files = fileInput?.files;

        if (!files) return;

        // Helper to update phase for a file
        const updatePhase = (filename: string, phase: UploadProgress['phase'], progress: number) => {
            setUploadQueue(prev =>
                prev.map(item =>
                    item.filename === filename
                        ? { ...item, phase, progress, status: phase === "done" ? "success" : "uploading" }
                        : item
                )
            );
        };

        const updateError = (filename: string, errorMsg: string) => {
            setUploadQueue(prev =>
                prev.map(item =>
                    item.filename === filename
                        ? { ...item, status: "error" as const, error: errorMsg }
                        : item
                )
            );
        };

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const filename = file.name;

            try {
                // Phase 1: Uploading
                updatePhase(filename, "uploading", 10);

                const formData = new FormData();
                formData.append("file", file);

                // Start Upload
                const res = await fetch(`${API_URL}/api/documents/upload`, {
                    method: "POST",
                    body: formData,
                });

                if (res.status === 202) {
                    const data = await res.json();
                    const taskId = data.task_id;

                    // Poll for status
                    let isProcessing = true;
                    while (isProcessing) {
                        await new Promise(r => setTimeout(r, 1000)); // Poll every 1s

                        const statusRes = await fetch(`${API_URL}/api/documents/${taskId}/status`);
                        if (!statusRes.ok) throw new Error("Status check failed");

                        const statusData = await statusRes.json();

                        switch (statusData.status) {
                            case "queued":
                                updatePhase(filename, "waiting", 15);
                                break;
                            case "starting":
                                updatePhase(filename, "uploading", 20);
                                break;
                            case "saving":
                                updatePhase(filename, "storing", 30);
                                break;
                            case "parsing":
                                updatePhase(filename, "parsing", 50);
                                break;
                            case "chunking":
                                updatePhase(filename, "chunking", 70);
                                break;
                            case "embedding":
                                updatePhase(filename, "embedding", 90);
                                break;
                            case "completed":
                                updatePhase(filename, "done", 100);
                                isProcessing = false;
                                break;
                            case "failed":
                                updateError(filename, statusData.error || "Processing failed");
                                isProcessing = false;
                                break;
                        }
                    }

                } else {
                    const error = await res.json();
                    updateError(filename, error.detail || "Upload fehlgeschlagen");
                }
            } catch (e) {
                console.error(e);
                updateError(filename, "Netzwerkfehler");
            }
        }

        setIsUploading(false);
        loadDocuments();
    };

    // Close panel and reset
    const closeUploadModal = () => {
        if (isUploading) return; // Don't close while uploading
        setShowUploadModal(false);
        setUploadQueue([]);
        const fileInput = document.getElementById('panel-file-input') as HTMLInputElement;
        if (fileInput) fileInput.value = "";
    };

    // Drag and drop handlers
    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        handleFileSelect(e.dataTransfer.files);
    };

    // Search documents
    const handleSearch = async () => {
        if (!searchQuery.trim()) return;
        setIsLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/documents/search`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: searchQuery, limit: 10 }),
            });
            const data = await res.json();
            setSearchResults(data);
        } catch (error) {
            console.error("Search failed:", error);
        } finally {
            setIsLoading(false);
        }
    };

    // Delete document
    const deleteDocument = async (docId: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!confirm("Dokument wirklich löschen?")) return;
        try {
            await fetch(`${API_URL}/api/documents/${docId}`, { method: "DELETE" });
            loadDocuments();
        } catch (error) {
            console.error("Delete failed:", error);
        }
    };

    // Download file
    const downloadFile = (docId: string) => {
        window.open(`${API_URL}/api/documents/${docId}/download`, '_blank');
    };

    // Get unique documents (group by filename, show only first chunk)
    const uniqueDocuments = documents
        .filter((doc: Document) => {
            // Filter by selected category if one is selected
            if (selectedCategory === null) return true;
            if (selectedCategory === "Allgemein") {
                return !doc.category || doc.category === "Allgemein";
            }
            return doc.category === selectedCategory;
        })
        .reduce((acc: Document[], doc: Document) => {
            if (!acc.find((d: Document) => d.filename === doc.filename)) {
                acc.push(doc);
            }
            return acc;
        }, [] as Document[]);

    // Delete confirmation modal state
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [deleteTarget, setDeleteTarget] = useState<{ id: string; filename: string } | null>(null);

    // Show delete confirmation
    const confirmDelete = (docId: string, filename: string, e: React.MouseEvent) => {
        e.stopPropagation();
        setDeleteTarget({ id: docId, filename });
        setShowDeleteConfirm(true);
    };

    // Execute delete
    const executeDelete = async () => {
        if (!deleteTarget) return;
        try {
            await fetch(`${API_URL}/api/documents/${deleteTarget.id}`, { method: "DELETE" });
            loadDocuments();
        } catch (error) {
            console.error("Delete failed:", error);
        } finally {
            setShowDeleteConfirm(false);
            setDeleteTarget(null);
        }
    };

    return (
        <div className="flex flex-col h-full overflow-hidden">
            {/* Page Header */}
            <div className="flex items-center justify-between mb-6 flex-shrink-0">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Dokumentenverwaltung</h1>
                    <p className="text-sm text-slate-500">RAG Wissensbasis • Qdrant Vector DB • {uniqueDocuments.length} Dokumente</p>
                </div>
                <div className="flex items-center gap-3">
                    <a
                        href="http://localhost:6333/dashboard"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2.5 bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-xl font-medium hover:from-purple-600 hover:to-indigo-700 transition-all shadow-lg shadow-purple-500/25 flex items-center gap-2"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        Qdrant
                    </a>

                    {/* Compact Sync Indicator */}
                    <button
                        onClick={syncStorage}
                        disabled={isSyncing}
                        className={`p-2.5 rounded-xl transition-all ${isSyncing
                            ? 'bg-slate-200 text-slate-400'
                            : syncResult?.in_sync
                                ? 'bg-green-100 text-green-600 hover:bg-green-200'
                                : 'bg-amber-100 text-amber-600 hover:bg-amber-200'
                            }`}
                        title={syncResult?.in_sync ? 'Speicher synchron' : 'Klicken zum Synchronisieren'}
                    >
                        {isSyncing ? (
                            <div className="w-5 h-5 animate-spin rounded-full border-2 border-slate-400 border-t-transparent" />
                        ) : (
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                        )}
                    </button>
                </div>
            </div>

            {/* Search Bar */}
            <div className="mb-6 flex gap-2 flex-shrink-0">
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                    placeholder="Semantische Suche in allen Dokumenten..."
                    className="flex-1 px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                />
                <button
                    onClick={handleSearch}
                    disabled={isLoading}
                    className="px-6 py-3 bg-slate-900 text-white rounded-xl hover:bg-slate-800 disabled:opacity-50 font-medium"
                >
                    Suchen
                </button>
            </div>

            {/* Main Content with Sidebar */}
            <div className="flex-1 flex gap-4 overflow-hidden">
                {/* Category Sidebar */}
                {showCategorySidebar && (
                    <div className="w-64 flex-shrink-0 bg-white rounded-xl border border-slate-200 p-4 overflow-y-auto">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="text-sm font-semibold text-slate-700">Kategorien</h3>
                            <div className="flex items-center gap-1">
                                <button
                                    onClick={() => setShowCreateCategoryModal(true)}
                                    className="text-blue-500 hover:text-blue-700 p-1"
                                    title="Neue Kategorie"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                    </svg>
                                </button>
                                <button
                                    onClick={() => setShowCategorySidebar(false)}
                                    className="text-slate-400 hover:text-slate-600 p-1"
                                    title="Sidebar schließen"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        </div>

                        {/* All Documents */}
                        <button
                            onClick={() => setSelectedCategory(null)}
                            className={`w-full text-left px-3 py-2 rounded-lg text-sm mb-1 transition-colors ${selectedCategory === null
                                ? 'bg-blue-100 text-blue-700 font-medium'
                                : 'hover:bg-slate-100 text-slate-600'
                                }`}
                        >
                            📁 Alle Dokumente
                            <span className="ml-auto float-right text-xs text-slate-400">
                                {documents.filter((d, i, arr) => arr.findIndex(x => x.filename === d.filename) === i).length}
                            </span>
                        </button>

                        <div className="h-px bg-slate-200 my-2"></div>

                        {/* Category List with Edit/Delete */}
                        {categories.length > 0 ? (
                            categories.map((cat) => (
                                <div key={cat.path} className="group relative">
                                    {editingCategory === cat.path ? (
                                        // Inline Edit Mode
                                        <div className="flex items-center gap-1 px-2 py-1">
                                            <input
                                                type="text"
                                                value={editCategoryName}
                                                onChange={(e) => setEditCategoryName(e.target.value)}
                                                onKeyDown={(e) => {
                                                    if (e.key === 'Enter') renameCategory(cat.path, editCategoryName);
                                                    if (e.key === 'Escape') setEditingCategory(null);
                                                }}
                                                className="flex-1 px-2 py-1 text-sm border rounded"
                                                autoFocus
                                            />
                                            <button
                                                onClick={() => renameCategory(cat.path, editCategoryName)}
                                                className="text-green-600 hover:text-green-800 p-1"
                                            >
                                                ✓
                                            </button>
                                            <button
                                                onClick={() => setEditingCategory(null)}
                                                className="text-red-500 hover:text-red-700 p-1"
                                            >
                                                ✕
                                            </button>
                                        </div>
                                    ) : (
                                        // Normal Display Mode
                                        <button
                                            onClick={() => setSelectedCategory(cat.path)}
                                            className={`w-full text-left px-3 py-2 rounded-lg text-sm mb-1 transition-colors flex items-center ${selectedCategory === cat.path
                                                ? 'bg-blue-100 text-blue-700 font-medium'
                                                : 'hover:bg-slate-100 text-slate-600'
                                                }`}
                                        >
                                            <span className="flex-1 truncate">📂 {cat.name}</span>
                                            <span className="text-xs text-slate-400 mr-1">{cat.document_count}</span>

                                            {/* Edit/Delete buttons (visible on hover) */}
                                            <div className="hidden group-hover:flex items-center gap-0.5">
                                                <span
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setEditingCategory(cat.path);
                                                        setEditCategoryName(cat.name);
                                                    }}
                                                    className="text-slate-400 hover:text-blue-600 p-0.5 cursor-pointer"
                                                    title="Umbenennen"
                                                >
                                                    ✏️
                                                </span>
                                                <span
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setCategoryToDelete(cat.path);
                                                    }}
                                                    className="text-slate-400 hover:text-red-600 p-0.5 cursor-pointer"
                                                    title="Löschen"
                                                >
                                                    🗑️
                                                </span>
                                            </div>
                                        </button>
                                    )}
                                </div>
                            ))
                        ) : (
                            <p className="text-xs text-slate-400 px-3 py-2">
                                Noch keine Kategorien
                            </p>
                        )}
                    </div>
                )}

                {/* Toggle Sidebar Button (when hidden) */}
                {!showCategorySidebar && (
                    <button
                        onClick={() => setShowCategorySidebar(true)}
                        className="flex-shrink-0 w-10 bg-white rounded-xl border border-slate-200 flex items-center justify-center hover:bg-slate-50"
                        title="Kategorien anzeigen"
                    >
                        <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                        </svg>
                    </button>
                )}

                {/* Document Grid */}
                <div className="flex-1 overflow-auto">
                    {isLoading ? (
                        <div className="flex justify-center py-12">
                            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {uniqueDocuments.map((doc) => (
                                <div
                                    key={doc.doc_id}
                                    onClick={() => openViewer(doc.doc_id)}
                                    className="bg-white rounded-2xl border border-slate-200 p-5 cursor-pointer hover:shadow-lg hover:border-blue-300 transition-all group"
                                >
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-xl flex items-center justify-center">
                                            <span className="text-sm font-bold text-blue-600 uppercase">{doc.doc_type}</span>
                                        </div>
                                        <button
                                            onClick={(e) => confirmDelete(doc.doc_id, doc.filename, e)}
                                            className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
                                            title="Dokument löschen"
                                        >
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </div>
                                    <h3 className="font-semibold text-slate-900 mb-1 truncate">{doc.filename}</h3>
                                    <p className="text-xs text-slate-500 line-clamp-2">{doc.content_preview}</p>
                                    <div className="mt-3 flex items-center gap-2 text-xs text-slate-400">
                                        <span>{new Date(doc.created_at || "").toLocaleDateString("de-DE")}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Delete Confirmation Modal */}
            {showDeleteConfirm && deleteTarget && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
                        <div className="flex items-center gap-4 mb-4">
                            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-slate-900">Dokument löschen?</h3>
                                <p className="text-sm text-slate-500">Diese Aktion kann nicht rückgängig gemacht werden.</p>
                            </div>
                        </div>
                        <div className="bg-slate-50 rounded-lg p-3 mb-6">
                            <p className="text-sm font-medium text-slate-700 truncate">{deleteTarget.filename}</p>
                            <p className="text-xs text-slate-500">Dokument und alle zugehörigen Chunks werden gelöscht</p>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={() => setShowDeleteConfirm(false)}
                                className="flex-1 px-4 py-2.5 border border-slate-300 text-slate-700 rounded-xl hover:bg-slate-50 font-medium"
                            >
                                Abbrechen
                            </button>
                            <button
                                onClick={executeDelete}
                                className="flex-1 px-4 py-2.5 bg-red-600 text-white rounded-xl hover:bg-red-700 font-medium"
                            >
                                Löschen
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Fullscreen Document Viewer */}
            {showViewer && (() => {
                // Get document index for navigation
                const currentDocId = viewerDoc?.doc_id;
                const docIndex = documents.findIndex(d => d.doc_id === currentDocId);
                const hasPrev = docIndex > 0;
                const hasNext = docIndex < documents.length - 1 && docIndex !== -1;

                // Extract title from metadata or filename
                const docTitle = viewerDoc?.metadata?.title ||
                    String(viewerDoc?.metadata?.filename || "Dokument").replace(/\.[^/.]+$/, "");

                return (
                    <div className="fixed inset-0 bg-white z-50 flex flex-col">
                        {/* Enhanced Viewer Header */}
                        <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white">
                            {/* Top Row - Title & Actions */}
                            <div className="px-6 py-3 flex items-center justify-between border-b border-slate-700/50">
                                <div className="flex items-center gap-4">
                                    <button
                                        onClick={() => setShowViewer(false)}
                                        className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
                                        title="Schließen"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                    <div className="flex items-center gap-3">
                                        <span className="px-2.5 py-1 bg-blue-600 text-white rounded-md text-xs font-bold uppercase tracking-wide">
                                            {String(viewerDoc?.metadata?.doc_type || "DOC")}
                                        </span>
                                        <h2 className="text-lg font-semibold truncate max-w-md text-white" title={String(docTitle)}>
                                            {String(docTitle)}
                                        </h2>
                                    </div>
                                </div>

                                {/* Navigation & Actions */}
                                <div className="flex items-center gap-3">
                                    {/* Prev/Next Navigation */}
                                    {documents.length > 1 && (
                                        <div className="flex items-center gap-1 mr-4">
                                            <button
                                                onClick={() => hasPrev && openViewer(documents[docIndex - 1].doc_id)}
                                                disabled={!hasPrev}
                                                className={`p-2 rounded-lg transition-colors ${hasPrev ? 'hover:bg-slate-700 text-white' : 'text-slate-500 cursor-not-allowed'}`}
                                                title="Vorheriges Dokument"
                                            >
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                                                </svg>
                                            </button>
                                            <span className="text-sm text-slate-400 px-2">
                                                {docIndex + 1} / {documents.length}
                                            </span>
                                            <button
                                                onClick={() => hasNext && openViewer(documents[docIndex + 1].doc_id)}
                                                disabled={!hasNext}
                                                className={`p-2 rounded-lg transition-colors ${hasNext ? 'hover:bg-slate-700 text-white' : 'text-slate-500 cursor-not-allowed'}`}
                                                title="Nächstes Dokument"
                                            >
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                </svg>
                                            </button>
                                        </div>
                                    )}

                                    <button
                                        onClick={() => viewerDoc && downloadFile(viewerDoc.doc_id)}
                                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                        </svg>
                                        Download
                                    </button>
                                </div>
                            </div>

                            {/* Metadata Row */}
                            <div className="px-6 py-2 flex items-center gap-6 text-sm text-slate-300 bg-slate-800/50">
                                {viewerDoc?.metadata?.page_count != null ? (
                                    <span className="flex items-center gap-1.5">
                                        <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                        </svg>
                                        {String(viewerDoc.metadata.page_count)} Seiten
                                    </span>
                                ) : null}
                                {viewerDoc?.metadata?.word_count != null ? (
                                    <span className="flex items-center gap-1.5">
                                        <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                                        </svg>
                                        {Number(viewerDoc.metadata.word_count).toLocaleString()} Wörter
                                    </span>
                                ) : null}
                                {chunks.length > 0 && (
                                    <span className="flex items-center gap-1.5">
                                        <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                                        </svg>
                                        {chunks.length} Chunks
                                    </span>
                                )}
                                {originalFile?.size_bytes && (
                                    <span className="flex items-center gap-1.5">
                                        <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                                        </svg>
                                        {(originalFile.size_bytes / 1024 / 1024).toFixed(2)} MB
                                    </span>
                                )}
                                {viewerDoc?.metadata?.created_at != null ? (
                                    <span className="flex items-center gap-1.5 text-slate-400">
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                        </svg>
                                        {new Date(String(viewerDoc.metadata.created_at)).toLocaleDateString('de-DE')}
                                    </span>
                                ) : null}
                            </div>
                        </div>

                        {/* Viewer Content - Split View */}
                        {loadingViewer ? (
                            <div className="flex-1 flex items-center justify-center">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                            </div>
                        ) : (
                            <div className="flex-1 flex overflow-hidden">
                                {/* Left - Original Document */}
                                <div className="flex-1 border-r border-slate-200 flex flex-col">
                                    <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
                                        <h3 className="font-medium text-slate-900">Original Dokument</h3>
                                    </div>
                                    <div className="flex-1 overflow-auto p-4 bg-slate-100">
                                        {originalFile ? (() => {
                                            // Determine the source URL - prefer presigned URL for large files
                                            const fileUrl = originalFile.presigned_url || originalFile.data_url;
                                            const fileSizeKB = originalFile.size_bytes ? Math.round(originalFile.size_bytes / 1024) : 0;

                                            return (
                                                <div className="bg-white rounded-lg shadow-sm h-full">
                                                    {originalFile.mime_type.startsWith('image/') ? (
                                                        <img src={fileUrl} alt="Original" className="max-w-full h-auto" />
                                                    ) : originalFile.mime_type === 'application/pdf' ? (
                                                        <>
                                                            {fileUrl ? (
                                                                <iframe
                                                                    src={fileUrl}
                                                                    className="w-full h-full min-h-[700px]"
                                                                    title="PDF Viewer"
                                                                />
                                                            ) : (
                                                                <div className="flex items-center justify-center h-full text-slate-500 p-8">
                                                                    <div className="text-center">
                                                                        <p className="mb-2">PDF zu groß für Vorschau</p>
                                                                        <p className="text-xs text-slate-400 mb-4">{fileSizeKB} KB</p>
                                                                        <button
                                                                            onClick={() => viewerDoc && downloadFile(viewerDoc.doc_id)}
                                                                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                                                        >
                                                                            Herunterladen
                                                                        </button>
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </>
                                                    ) : ['application/xml', 'text/plain', 'text/markdown', 'application/json', 'text/html'].includes(originalFile.mime_type) ? (
                                                        <pre className="text-sm text-slate-700 p-6 whitespace-pre-wrap break-words font-mono overflow-auto h-full">
                                                            {(() => {
                                                                try {
                                                                    if (originalFile.data_url) {
                                                                        const base64 = originalFile.data_url.split(',')[1];
                                                                        return atob(base64);
                                                                    }
                                                                    return 'Keine Textvorschau verfügbar';
                                                                } catch {
                                                                    return 'Fehler beim Dekodieren';
                                                                }
                                                            })()}
                                                        </pre>
                                                    ) : (
                                                        <div className="flex items-center justify-center h-full text-slate-500 p-8">
                                                            <div className="text-center w-full">
                                                                <p className="mb-2 font-medium">Vorschau nicht verfügbar</p>
                                                                <p className="text-xs text-slate-400 mb-4">Das Originaldokument konnte nicht geladen werden.</p>
                                                                <button
                                                                    onClick={() => viewerDoc && downloadFile(viewerDoc.doc_id)}
                                                                    className="text-blue-600 hover:underline"
                                                                >
                                                                    Herunterladen
                                                                </button>
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            );
                                        })() : (
                                            <div className="flex items-center justify-center h-full text-slate-500 p-8">
                                                <div className="text-center w-full">
                                                    <p className="mb-4">Kein Original verfügbar</p>
                                                    <p className="text-xs text-slate-400">Für dieses Dokument ist keine Vorschau vorhanden.</p>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Right - Chunks */}
                                <div className="w-96 flex flex-col bg-slate-50">
                                    <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
                                        <h3 className="font-medium text-slate-900">RAG Chunks ({chunks.length})</h3>
                                    </div>
                                    <div className="flex-1 overflow-auto p-4 space-y-3">
                                        {chunks.length > 0 ? chunks.map((chunk, idx) => (
                                            <ChunkCard key={chunk.doc_id} chunk={chunk} index={idx} loadContent={loadChunkContent} />
                                        )) : (
                                            <p className="text-slate-500 text-sm text-center py-4">Keine Chunks gefunden</p>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                );
            })()}

            {/* Bottom-Right Upload FAB + Drawer */}
            {!showUploadModal && !showViewer && (
                <button
                    onClick={() => setShowUploadModal(true)}
                    className="fixed bottom-6 right-6 z-40 w-14 h-14 bg-gradient-to-r from-slate-700 to-slate-900 text-white rounded-full shadow-2xl shadow-slate-900/40 hover:scale-110 hover:shadow-slate-900/60 transition-all flex items-center justify-center group"
                    title="Dokument hochladen"
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                </button>
            )}

            {showUploadModal && (
                <div
                    className={`fixed z-50 transition-all duration-300 ${isUploadMinimized
                        ? "bottom-6 right-6 w-80"
                        : "bottom-6 right-6 w-[420px]"
                        }`}
                >
                    {/* Minimized View */}
                    {isUploadMinimized ? (
                        <div
                            onClick={() => setIsUploadMinimized(false)}
                            className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-2xl shadow-2xl p-4 cursor-pointer hover:scale-[1.02] transition-all"
                        >
                            <div className="flex items-center gap-3">
                                {isUploading ? (
                                    <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                                        <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                                    </div>
                                ) : uploadQueue.every(f => f.status === "success") ? (
                                    <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                                        <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                    </div>
                                ) : (
                                    <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                                        <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                        </svg>
                                    </div>
                                )}
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium truncate">
                                        {isUploading
                                            ? `${uploadQueue.find(f => f.status === "uploading")?.filename || "Verarbeite..."}`
                                            : uploadQueue.every(f => f.status === "success")
                                                ? "Alle Uploads fertig ✓"
                                                : `${uploadQueue.length} Datei(en) bereit`}
                                    </p>
                                    {isUploading && (
                                        <>
                                            <p className="text-xs text-slate-400 mt-0.5">
                                                {PROCESSING_PHASES.find(p => p.key === uploadQueue.find(f => f.status === "uploading")?.phase)?.description || "Verarbeite..."}
                                            </p>
                                            <div className="mt-1.5 h-1.5 bg-white/10 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-gradient-to-r from-blue-400 to-indigo-400 transition-all"
                                                    style={{ width: `${uploadQueue.find(f => f.status === "uploading")?.progress || 0}%` }}
                                                />
                                            </div>
                                        </>
                                    )}
                                </div>
                                <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                                </svg>
                            </div>
                        </div>
                    ) : (
                        /* Expanded Drawer */
                        <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden max-h-[70vh] flex flex-col">
                            {/* Header */}
                            <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white px-5 py-4 flex items-center justify-between">
                                <div>
                                    <h3 className="font-semibold">Dokumente hochladen</h3>
                                    <p className="text-xs text-slate-400 mt-0.5">In Qdrant indexieren</p>
                                </div>
                                <div className="flex items-center gap-1">
                                    {isUploading && (
                                        <button
                                            onClick={() => setIsUploadMinimized(true)}
                                            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                                            title="Minimieren"
                                        >
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                            </svg>
                                        </button>
                                    )}
                                    <button
                                        onClick={closeUploadModal}
                                        disabled={isUploading}
                                        className="p-2 hover:bg-white/10 rounded-lg transition-colors disabled:opacity-50"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                            </div>

                            {/* Drop Zone */}
                            <div className="p-4">
                                <label
                                    className={`relative flex flex-col items-center justify-center w-full h-28 border-2 border-dashed rounded-xl cursor-pointer transition-all ${dragActive
                                        ? "border-blue-500 bg-blue-50"
                                        : "border-slate-300 hover:bg-slate-50 hover:border-blue-400"
                                        }`}
                                    onDragEnter={handleDrag}
                                    onDragLeave={handleDrag}
                                    onDragOver={handleDrag}
                                    onDrop={handleDrop}
                                >
                                    <div className="flex flex-col items-center justify-center">
                                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-2 ${dragActive ? "bg-blue-500" : "bg-gradient-to-br from-blue-500 to-indigo-600"
                                            }`}>
                                            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                            </svg>
                                        </div>
                                        <p className="text-xs text-slate-600">
                                            <span className="text-blue-600 font-medium">Klicken</span> oder Dateien ziehen
                                        </p>
                                    </div>
                                    <input
                                        id="panel-file-input"
                                        type="file"
                                        className="hidden"
                                        multiple
                                        accept=".pdf,.docx,.doc,.pptx,.ppt,.xml,.txt,.md,.json,.html,.png,.jpg,.jpeg"
                                        onChange={(e) => handleFileSelect(e.target.files)}
                                    />
                                </label>
                            </div>

                            {/* File Queue */}
                            {uploadQueue.length > 0 && (
                                <div className="flex-1 overflow-auto px-4 pb-4 space-y-3 max-h-60">
                                    {uploadQueue.map((item, idx) => (
                                        <div key={idx} className="bg-slate-50 rounded-xl p-3 border border-slate-100">
                                            <div className="flex items-center gap-3">
                                                <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${item.status === "error" ? "bg-red-100" :
                                                    item.status === "success" ? "bg-green-100" :
                                                        "bg-blue-100"
                                                    }`}>
                                                    {item.status === "error" ? (
                                                        <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                        </svg>
                                                    ) : item.status === "success" ? (
                                                        <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                                        </svg>
                                                    ) : item.status === "uploading" ? (
                                                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent" />
                                                    ) : (
                                                        <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                        </svg>
                                                    )}
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-sm font-medium text-slate-800 truncate">{item.filename}</p>
                                                    <p className="text-xs text-slate-500">
                                                        {item.status === "pending" && "Bereit"}
                                                        {item.status === "uploading" && PROCESSING_PHASES.find(p => p.key === item.phase)?.description}
                                                        {item.status === "success" && "Indexiert ✓"}
                                                        {item.status === "error" && (item.error || "Fehler")}
                                                    </p>
                                                </div>
                                            </div>
                                            {item.status === "uploading" && (
                                                <div className="mt-2 h-1 bg-slate-200 rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all"
                                                        style={{ width: `${item.progress}%` }}
                                                    />
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Footer */}
                            <div className="border-t border-slate-200 p-4">
                                <button
                                    onClick={() => {
                                        startUpload();
                                        setIsUploadMinimized(true);
                                    }}
                                    disabled={uploadQueue.length === 0 || isUploading || uploadQueue.every(f => f.status === "success")}
                                    className="w-full px-4 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl font-medium hover:from-blue-600 hover:to-indigo-700 transition-all shadow-lg shadow-blue-500/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                >
                                    {isUploading ? (
                                        <>
                                            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                                            <span>Verarbeite...</span>
                                        </>
                                    ) : uploadQueue.every(f => f.status === "success") ? (
                                        <>
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                            </svg>
                                            <span>Fertig</span>
                                        </>
                                    ) : (
                                        <>
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                                            </svg>
                                            <span>Hochladen &amp; Minimieren</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Create Category Modal */}
            {showCreateCategoryModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
                        <h3 className="text-lg font-semibold text-slate-900 mb-4">Neue Kategorie</h3>
                        <input
                            type="text"
                            value={newCategoryName}
                            onChange={(e) => setNewCategoryName(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && createCategory()}
                            placeholder="Kategoriename..."
                            className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                            autoFocus
                        />
                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={() => {
                                    setShowCreateCategoryModal(false);
                                    setNewCategoryName("");
                                }}
                                className="flex-1 px-4 py-2.5 border border-slate-300 text-slate-700 rounded-xl hover:bg-slate-50 font-medium"
                            >
                                Abbrechen
                            </button>
                            <button
                                onClick={createCategory}
                                disabled={!newCategoryName.trim()}
                                className="flex-1 px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 font-medium disabled:opacity-50"
                            >
                                Erstellen
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Delete Category Confirmation Modal */}
            {categoryToDelete && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
                        <div className="flex items-center gap-4 mb-4">
                            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-slate-900">Kategorie löschen?</h3>
                                <p className="text-sm text-slate-500">Dokumente werden zu &quot;Allgemein&quot; verschoben.</p>
                            </div>
                        </div>
                        <div className="bg-slate-50 rounded-lg p-3 mb-6">
                            <p className="text-sm font-medium text-slate-700">📂 {categoryToDelete}</p>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={() => setCategoryToDelete(null)}
                                className="flex-1 px-4 py-2.5 border border-slate-300 text-slate-700 rounded-xl hover:bg-slate-50 font-medium"
                            >
                                Abbrechen
                            </button>
                            <button
                                onClick={() => deleteCategory(categoryToDelete)}
                                className="flex-1 px-4 py-2.5 bg-red-600 text-white rounded-xl hover:bg-red-700 font-medium"
                            >
                                Löschen
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

// Chunk Card Component
function ChunkCard({ chunk, index, loadContent }: { chunk: DocumentChunk; index: number; loadContent: (id: string) => Promise<string> }) {
    const [expanded, setExpanded] = useState(false);
    const [content, setContent] = useState<string>(chunk.content || "");
    const [loading, setLoading] = useState(!chunk.content);

    // Auto-load content on mount if not provided
    useEffect(() => {
        if (!chunk.content && chunk.doc_id) {
            setLoading(true);
            loadContent(chunk.doc_id).then(loadedContent => {
                setContent(loadedContent);
                setLoading(false);
            }).catch(() => {
                setContent("Fehler beim Laden");
                setLoading(false);
            });
        }
    }, [chunk.doc_id, chunk.content, loadContent]);

    return (
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                    <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold">
                        {index + 1}
                    </span>
                    <span className="text-xs font-medium text-slate-500">
                        Chunk {index + 1}{chunk.total_chunks > 0 ? ` von ${chunk.total_chunks}` : ""}
                    </span>
                </div>
                <button
                    onClick={() => setExpanded(!expanded)}
                    className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                >
                    {expanded ? "Weniger" : "Mehr anzeigen"}
                </button>
            </div>
            {loading ? (
                <div className="flex items-center gap-2 py-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                    <span className="text-xs text-slate-400">Lade Inhalt...</span>
                </div>
            ) : (
                <p className={`text-sm text-slate-700 leading-relaxed ${expanded ? "" : "line-clamp-3"}`}>
                    {content || "Kein Inhalt"}
                </p>
            )}
        </div>
    );
}
