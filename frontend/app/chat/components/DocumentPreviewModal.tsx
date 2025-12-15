import { useEffect, useState } from "react";

interface DocumentPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  docId: string;
  filename: string;
  initialContent?: string;
}

export default function DocumentPreviewModal({
  isOpen,
  onClose,
  docId,
  filename,
  initialContent,
}: DocumentPreviewModalProps) {
  const [content, setContent] = useState<string | null>("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [viewerKey, setViewerKey] = useState(0);

  useEffect(() => {
    if (isOpen && docId) {
      loadOriginal();
      setSearchQuery("");
      setSearchResults([]);
      setViewerKey(0);
    } else {
      // Reset state when closed
      setContent("");
      setError(null);
      setPdfUrl(null);
      setSearchQuery("");
      setSearchResults([]);
      setViewerKey(0);
    }
  }, [isOpen, docId]);

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (searchQuery.trim()) {
        performSearch(searchQuery);
      } else {
        setSearchResults([]);
      }
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery, docId]);

  const performSearch = async (query: string) => {
    setIsSearching(true);
    try {
      const res = await fetch("http://localhost:8000/api/documents/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: query,
          limit: 10,
          doc_id: docId,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setSearchResults(data);
      }
    } catch (err) {
      console.error("Search failed", err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleResultClick = (pageNumber: number) => {
    if (pdfUrl) {
      // We need one clean URL without existing fragments
      const baseUrl = pdfUrl.split("#")[0];
      const newUrl = `${baseUrl}#page=${pageNumber}`;
      setPdfUrl(newUrl);
      setViewerKey((prev) => prev + 1); // Force re-render of iframe
    }
  };

  const loadOriginal = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Fetch original content
      const res = await fetch(
        `http://localhost:8000/api/documents/${docId}/original`,
      );
      if (!res.ok) throw new Error("Failed to load document");

      const data = await res.json();
      // data is base64 encoded file content usually

      // Check for binary/PDF types
      const isBinary =
        data.mime_type?.includes("pdf") ||
        data.mime_type?.includes("image") ||
        data.mime_type?.includes("octet-stream") ||
        filename.endsWith(".pdf") ||
        filename.endsWith(".png") ||
        filename.endsWith(".jpg");

      if (isBinary) {
        // Determine specific binary type
        if (data.mime_type?.includes("pdf") || filename.endsWith(".pdf")) {
          try {
            // Create Blob URL for PDF iframe
            const byteCharacters = atob(data.data);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
              byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: "application/pdf" });
            const url = URL.createObjectURL(blob);
            setPdfUrl(url);
            setContent(null);
            setError(null);
          } catch (e) {
            console.error("PDF Blob creation failed", e);
            // Fallback to text if blob fails
            if (initialContent) {
              setContent(initialContent);
              setError("PDF Preview failed. Showing extracted text.");
            } else {
              setContent("Error creating PDF preview.");
              setError(null);
            }
          }
        } else if (initialContent) {
          setContent(initialContent);
          setError(
            "Original format (" +
              (data.mime_type || "binary") +
              ") cannot be previewed directly. Showing extracted text used for search.",
          );
        } else {
          setContent(
            "Preview not available for this file type. Please download to view.",
          );
          setError(null);
        }
      } else {
        // Try to decode text
        try {
          const text = atob(data.data);
          setContent(text);
          setPdfUrl(null);
        } catch (e) {
          // If decode fails, use initialContent
          if (initialContent) {
            setContent(initialContent);
            setError("Could not decode file content. Showing extracted text.");
          } else {
            setContent("Error decoding file content or binary file.");
          }
        }
      }
    } catch (err) {
      console.error(err);
      // If original fetch fails, fall back to initial snippet or error
      if (initialContent) {
        setContent(initialContent);
        setError("Could not load full document. Showing extracted text.");
      } else {
        setError("Could not load document.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Cleanup Blob URL on unmount or new doc
  useEffect(() => {
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [pdfUrl, docId]); // Add docId dependency so it doesn't revoke on hash change if we use same blob

  const handleDownload = () => {
    window.open(
      `http://localhost:8000/api/documents/${docId}/download`,
      "_blank",
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl w-full max-w-[95vw] h-[95vh] flex flex-col shadow-2xl overflow-hidden relative">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/50">
          <div className="flex items-center gap-4 flex-1 mr-4">
            <div>
              <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <span className="p-1.5 bg-white rounded-lg border border-slate-200 shadow-sm text-blue-600">
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </span>
                <span className="truncate max-w-md" title={filename}>
                  {filename}
                </span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5 ml-11">
                Document Viewer
              </p>
            </div>

            {/* Integrated Search Bar */}
            <div className="flex-1 max-w-xl mx-auto hidden md:block">
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg
                    className={`h-5 w-5 transition-colors ${isSearching ? "text-blue-500 animate-pulse" : "text-slate-400 group-focus-within:text-blue-500"}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                </div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2 border border-slate-200 rounded-xl leading-5 bg-white placeholder-slate-400 focus:outline-none focus:placeholder-slate-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 sm:text-sm transition-all shadow-sm"
                  placeholder="In Dokument suchen..."
                />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Download Button added to header for easier access */}
            <button
              onClick={handleDownload}
              className="p-2 hover:bg-slate-100 rounded-lg text-blue-600 font-medium text-sm flex items-center gap-2 transition-colors mr-2"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Download
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-100 rounded-full text-slate-400 hover:text-slate-600 transition-colors"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Content Area with Search Results Sidebar */}
        <div className="flex flex-1 overflow-hidden relative">
          {/* Main Document Content */}
          <div className="flex-1 overflow-hidden bg-white relative h-full">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-3">
                <div className="w-10 h-10 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
                <p className="text-sm font-medium">Lade Dokument...</p>
              </div>
            ) : (
              <div className="flex flex-col h-full">
                {error && !pdfUrl && (
                  <div className="m-4 mb-0 p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-center gap-2 text-amber-700 text-sm flex-shrink-0">
                    <svg
                      className="w-4 h-4 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    {error}
                  </div>
                )}

                {pdfUrl ? (
                  <iframe
                    key={viewerKey}
                    src={pdfUrl}
                    className="w-full h-full border-0"
                    title="PDF Preview"
                  />
                ) : (
                  <div className="prose prose-slate max-w-none flex-1 overflow-auto p-8">
                    <pre className="whitespace-pre-wrap font-sans text-slate-700 leading-relaxed text-base bg-transparent p-0 border-0">
                      {content}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Search Results Sidebar */}
          {searchResults.length > 0 && (
            <div className="w-80 border-l border-slate-200 bg-slate-50 overflow-y-auto hidden lg:block animate-in slide-in-from-right duration-200">
              <div className="p-4 border-b border-slate-200 flex items-center justify-between sticky top-0 bg-slate-50 z-10">
                <h4 className="font-semibold text-slate-700 text-sm">
                  Suchergebnisse
                </h4>
                <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                  {searchResults.length}
                </span>
              </div>
              <div className="p-3 space-y-3">
                {searchResults.map((result, idx) => (
                  <div
                    key={idx}
                    onClick={() => {
                      const page = result.metadata?.chunk_page_numbers?.[0];
                      if (page !== undefined) {
                        handleResultClick(page);
                      }
                    }}
                    className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm hover:border-blue-300 hover:shadow-md transition-all cursor-pointer group active:scale-[0.98]"
                  >
                    <div className="flex items-center justify-end mb-1">
                      {result.metadata?.chunk_page_numbers &&
                        result.metadata.chunk_page_numbers.length > 0 && (
                          <span className="text-xs text-blue-600 font-medium bg-blue-50 px-2 py-0.5 rounded">
                            Seite {result.metadata.chunk_page_numbers[0]}
                          </span>
                        )}
                    </div>
                    <p className="text-sm text-slate-600 line-clamp-3 leading-relaxed group-hover:text-slate-800">
                      {result.content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
