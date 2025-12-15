"use client";

import { useState, useEffect, useCallback } from "react";
import {
  FileText,
  Check,
  Search,
  X,
  Folder,
  Lock,
  Globe,
  Building,
} from "lucide-react";

interface Document {
  doc_id: string;
  filename: string;
  category: string;
  access_level?: string;
}

interface DocumentSelectorProps {
  isOpen: boolean;
  onClose: () => void;
  selectedDocIds: string[];
  onSelectionChange: (docIds: string[]) => void;
  apiUrl?: string;
}

const ACCESS_LEVEL_ICONS: Record<string, React.ReactNode> = {
  public: <Globe className="w-3.5 h-3.5 text-green-500" />,
  internal: <Building className="w-3.5 h-3.5 text-blue-500" />,
  restricted: <Lock className="w-3.5 h-3.5 text-amber-500" />,
  project: <Folder className="w-3.5 h-3.5 text-purple-500" />,
};

const ACCESS_LEVEL_LABELS: Record<string, string> = {
  public: "Öffentlich",
  internal: "Intern",
  restricted: "Eingeschränkt",
  project: "Projekt",
};

export default function DocumentSelector({
  isOpen,
  onClose,
  selectedDocIds,
  onSelectionChange,
  apiUrl = "http://localhost:8000",
}: DocumentSelectorProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const loadDocuments = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiUrl}/api/documents/accessible`);
      if (res.ok) {
        const data = await res.json();
        setDocuments(data.documents || []);
      }
    } catch (error) {
      console.error("Failed to load documents:", error);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  useEffect(() => {
    if (isOpen) {
      loadDocuments();
    }
  }, [isOpen, loadDocuments]);

  const toggleDocument = (docId: string) => {
    if (selectedDocIds.includes(docId)) {
      onSelectionChange(selectedDocIds.filter((id) => id !== docId));
    } else {
      onSelectionChange([...selectedDocIds, docId]);
    }
  };

  const selectAll = () => {
    onSelectionChange(filteredDocuments.map((d) => d.doc_id));
  };

  const clearAll = () => {
    onSelectionChange([]);
  };

  // Get unique categories
  const categories = [...new Set(documents.map((d) => d.category))].sort();

  // Filter documents
  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch =
      !searchTerm ||
      doc.filename.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory =
      !selectedCategory || doc.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/40 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden ring-1 ring-slate-900/5 flex flex-col max-h-[80vh]">
        {/* Header */}
        <div className="p-6 border-b border-slate-100">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
              <FileText className="w-6 h-6 text-indigo-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-slate-900">
                Dokumente auswählen
              </h3>
              <p className="text-sm text-slate-500">
                Welche Dokumente sollen als Kontext verwendet werden?
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-slate-400" />
            </button>
          </div>

          {/* Search and Filters */}
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Dokumente durchsuchen..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            <select
              value={selectedCategory || ""}
              onChange={(e) => setSelectedCategory(e.target.value || null)}
              className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Alle Kategorien</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Quick Actions */}
          <div className="flex gap-2 mt-3">
            <button
              onClick={selectAll}
              className="text-xs px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg transition-colors"
            >
              Alle auswählen
            </button>
            <button
              onClick={clearAll}
              className="text-xs px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg transition-colors"
            >
              Auswahl aufheben
            </button>
          </div>
        </div>

        {/* Document List */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : filteredDocuments.length === 0 ? (
            <div className="text-center py-12 text-slate-400">
              <FileText className="w-12 h-12 mx-auto mb-3 text-slate-200" />
              <p className="text-sm">Keine Dokumente gefunden</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredDocuments.map((doc) => {
                const isSelected = selectedDocIds.includes(doc.doc_id);
                const accessLevel = doc.access_level || "internal";

                return (
                  <button
                    key={doc.doc_id}
                    onClick={() => toggleDocument(doc.doc_id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-left ${
                      isSelected
                        ? "bg-indigo-50 ring-2 ring-indigo-400"
                        : "bg-slate-50 hover:bg-slate-100"
                    }`}
                  >
                    {/* Checkbox */}
                    <div
                      className={`w-5 h-5 rounded flex items-center justify-center transition-colors flex-shrink-0 ${
                        isSelected
                          ? "bg-indigo-600"
                          : "bg-white border-2 border-slate-300"
                      }`}
                    >
                      {isSelected && <Check className="w-3 h-3 text-white" />}
                    </div>

                    {/* Icon */}
                    <FileText
                      className={`w-4 h-4 flex-shrink-0 ${
                        isSelected ? "text-indigo-600" : "text-slate-400"
                      }`}
                    />

                    {/* Document Info */}
                    <div className="flex-1 min-w-0">
                      <span
                        className={`font-medium block truncate ${
                          isSelected ? "text-indigo-900" : "text-slate-700"
                        }`}
                      >
                        {doc.filename}
                      </span>
                      <span className="text-xs text-slate-400 flex items-center gap-2">
                        <Folder className="w-3 h-3" />
                        {doc.category}
                      </span>
                    </div>

                    {/* Access Level Badge */}
                    <div
                      className={`flex items-center gap-1.5 px-2 py-1 rounded-full text-xs ${
                        accessLevel === "public"
                          ? "bg-green-50 text-green-700"
                          : accessLevel === "internal"
                            ? "bg-blue-50 text-blue-700"
                            : accessLevel === "restricted"
                              ? "bg-amber-50 text-amber-700"
                              : "bg-purple-50 text-purple-700"
                      }`}
                    >
                      {ACCESS_LEVEL_ICONS[accessLevel]}
                      <span>{ACCESS_LEVEL_LABELS[accessLevel]}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-slate-50 px-6 py-4 border-t border-slate-100">
          <div className="flex items-center justify-between">
            <div className="text-sm text-slate-600">
              {selectedDocIds.length === 0 ? (
                <span className="flex items-center gap-2">
                  📚 <strong>Alle Dokumente</strong> werden verwendet
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  ✓ <strong>{selectedDocIds.length}</strong> Dokument(e)
                  ausgewählt
                </span>
              )}
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  onSelectionChange([]);
                  onClose();
                }}
                className="px-5 py-2.5 text-slate-600 hover:text-slate-900 font-medium hover:bg-white rounded-xl transition-all"
              >
                Alle verwenden
              </button>
              <button
                onClick={onClose}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium shadow-lg shadow-indigo-500/20 transition-all"
              >
                Bestätigen
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
