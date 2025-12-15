import { useState, useEffect } from "react";
import {
  X,
  FileText,
  Download,
  Calendar,
  HardDrive,
  Info,
  AlertTriangle,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";

interface DocumentViewerProps {
  isOpen: boolean;
  onClose: () => void;
  docId: string | null;
  apiUrl?: string;
}

export default function DocumentViewer({
  isOpen,
  onClose,
  docId,
  apiUrl = "http://localhost:8000",
}: DocumentViewerProps) {
  const [document, setDocument] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [originalFile, setOriginalFile] = useState<any>(null);
  const [chunks, setChunks] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && docId) {
      loadDocument(docId);
    } else {
      setDocument(null);
      setOriginalFile(null);
      setChunks([]);
      setError(null);
    }
  }, [isOpen, docId]);

  const loadDocument = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      // 1. Get Document Details
      const res = await fetch(`${apiUrl}/api/documents/${id}`);
      if (!res.ok) throw new Error("Document not found");
      const data = await res.json();
      setDocument(data);

      // 2. Try to get Original File (Presigned or Base64)
      const parentId = data.metadata?.parent_doc_id || data.doc_id || id;
      try {
        // Try presigned first
        let presignedRes = await fetch(
          `${apiUrl}/api/documents/${parentId}/presigned`,
        );
        if (!presignedRes.ok && parentId !== id) {
          presignedRes = await fetch(`${apiUrl}/api/documents/${id}/presigned`);
        }

        if (presignedRes.ok) {
          const pData = await presignedRes.json();
          if (pData.url) {
            setOriginalFile({ ...pData, storage: "minio" });
          } else if (pData.size_bytes && pData.size_bytes < 5 * 1024 * 1024) {
            // Small file fallback to base64
            const origRes = await fetch(
              `${apiUrl}/api/documents/${parentId}/original`,
            );
            if (origRes.ok) {
              const oData = await origRes.json();
              setOriginalFile(oData);
            }
          }
        } else {
          // Fallback base64
          const origRes = await fetch(
            `${apiUrl}/api/documents/${parentId}/original`,
          );
          if (origRes.ok) {
            const oData = await origRes.json();
            setOriginalFile(oData);
          }
        }
      } catch (e) {
        console.warn("Could not load original file:", e);
      }

      // 3. Load Chunks (Optional context)
      // skipping for minimalism unless requested, but helpful for debug
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Fehler beim Laden");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.95, opacity: 0, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-white w-full max-w-5xl h-[85vh] rounded-2xl shadow-2xl overflow-hidden flex flex-col"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/50">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h2 className="font-semibold text-slate-900 truncate max-w-md">
                  {document?.metadata?.filename || "Dokument"}
                </h2>
                <p className="text-xs text-slate-500 flex items-center gap-2">
                  <span>{document?.doc_id?.slice(0, 8)}</span>
                  {document?.metadata?.created_at && (
                    <>
                      <span>•</span>
                      <span>
                        {new Date(
                          document.metadata.created_at,
                        ).toLocaleDateString()}
                      </span>
                    </>
                  )}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {originalFile && (
                <a
                  href={`${apiUrl}/api/documents/${document?.doc_id}/download`}
                  target="_blank"
                  rel="noreferrer"
                  className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-slate-900 transition-colors"
                  title="Download"
                >
                  <Download className="w-5 h-5" />
                </a>
              )}
              <button
                onClick={onClose}
                className="p-2 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-red-500 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-hidden bg-slate-100 relative">
            {loading ? (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="flex flex-col items-center gap-3 text-slate-500">
                  <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                  <span className="text-sm font-medium">Lade Dokument...</span>
                </div>
              </div>
            ) : error ? (
              <div className="absolute inset-0 flex items-center justify-center p-8">
                <div className="text-center max-w-md">
                  <div className="w-12 h-12 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
                    <AlertTriangle className="w-6 h-6" />
                  </div>
                  <h3 className="font-bold text-slate-900 mb-2">
                    Fehler beim Laden
                  </h3>
                  <p className="text-slate-500 text-sm">{error}</p>
                </div>
              </div>
            ) : (
              <div className="h-full flex flex-col">
                {originalFile ? (
                  originalFile.mime_type === "application/pdf" ? (
                    <iframe
                      src={
                        originalFile.url ||
                        originalFile.presigned_url ||
                        originalFile.data_url
                      }
                      className="w-full h-full border-none"
                      title="PDF Viewer"
                    />
                  ) : originalFile.mime_type?.startsWith("image/") ? (
                    <div className="w-full h-full flex items-center justify-center p-8 overflow-auto">
                      <img
                        src={
                          originalFile.url ||
                          originalFile.presigned_url ||
                          originalFile.data_url
                        }
                        alt="Preview"
                        className="max-w-full max-h-full object-contain shadow-lg rounded-lg"
                      />
                    </div>
                  ) : (
                    <div className="w-full h-full p-8 overflow-auto">
                      <div className="bg-white shadow-sm rounded-xl p-8 max-w-3xl mx-auto min-h-full">
                        <pre className="whitespace-pre-wrap font-mono text-sm text-slate-700">
                          {document?.content || "Keine Vorschau verfügbar."}
                        </pre>
                      </div>
                    </div>
                  )
                ) : (
                  <div className="w-full h-full p-8 overflow-auto">
                    <div className="bg-white shadow-sm rounded-xl p-8 max-w-3xl mx-auto min-h-full">
                      <div className="prose prose-slate max-w-none">
                        <ReactMarkdown>
                          {document?.content || "*Kein Inhalt verfügbar*"}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
