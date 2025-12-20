"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import AppLayout from "../../components/AppLayout";
import ReactMarkdown from "react-markdown";
import {
  Upload,
  FileText,
  Plus,
  Cpu,
  CheckCircle,
  Clock,
  Download,
  X,
  Trash2,
  FolderOpen,
  Check,
  Database,
  Play,
  PenTool,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Beaker,
  Filter,
  Search,
  BarChart3,
  TrendingUp,
  CheckCircle2,
  XCircle,
  SkipForward,
} from "lucide-react";
import DocumentViewer from "../../components/DocumentViewer";
import DocumentSelector from "../../components/DocumentSelector";
import DDDChat from "../../components/DDDChat";
import ExcelJS from "exceljs";
import { saveAs } from "file-saver";
import { motion, AnimatePresence } from "framer-motion";
import {
  useTestExecutions,
  useTestStatistics,
  useSaveTestExecution,
  useBulkSaveTestExecutions,
  type TestExecution,
  type TestExecutionRequest,
} from "../../../lib/api/testing";

const API_URL = "http://localhost:8000";

interface Project {
  id: string;
  name: string;
  description: string;
  created_at: string;
}

interface TestCase {
  testNr: string;
  testinhalt: string;
  beschreibung: string;
  resultat: string;
  testdatum: string;
  buildId: string;
  tester: string;
  kommentar: string;
  vorbedingung?: string;
  schritte?: string;
  erwartetes_ergebnis?: string;
}

interface TestPlan {
  id: string;
  content: string;
  created_at: string;
  testCases?: TestCase[];
}

interface Document {
  doc_id: string;
  metadata: {
    filename: string;
    category?: string;
    created_at?: string;
    [key: string]: unknown;
  };
  linked_at?: string;
  processing_status?:
  | "queued"
  | "starting"
  | "saving"
  | "parsing"
  | "chunking"
  | "embedding"
  | "completed"
  | "failed"
  | "processing";
  processing_progress?: number;
  rag_enabled?: boolean;
}

interface Category {
  name: string;
  path: string;
  document_count: number;
}

// --- Types & Parsing ---

interface StructuredTestCase {
  test_id: string;
  title: string;
  description: string;
  preconditions: string;
  steps: string;
  expected_result: string;
}

interface GenerationStatus {
  status: "processing" | "completed" | "failed";
  stage?: string;
  progress?: number;
  message?: string;
  data?: {
    test_cases: StructuredTestCase[];
    introduction: string;
    summary: string;
  };
  error?: string;
}

interface ProcessedTestPlan extends TestPlan {
  isStructured: boolean;
  status: "processing" | "completed" | "failed";
  generationState?: GenerationStatus;
  testCases: TestCase[]; // Standardized internal format
}

function parseTestCases(content: string): TestCase[] {
  // Legacy Markdown Parser
  const testCases: TestCase[] = [];
  const tcBlockRegex =
    /###\s*(TC-\d{3}):\s*([^\n]+)\n([\s\S]*?)(?=###\s*TC-\d{3}:|##\s|$)/gi;
  let match;
  while ((match = tcBlockRegex.exec(content)) !== null) {
    testCases.push({
      testNr: match[1],
      testinhalt: match[2].trim(),
      beschreibung:
        match[3]?.match(/\*\*Beschreibung\*\*:\s*([^\n]+)/i)?.[1]?.trim() || "",
      resultat: "",
      testdatum: "",
      buildId: "",
      tester: "",
      kommentar: "",
    });
  }
  // Simple fallback if regex fails
  if (testCases.length === 0) {
    const lines = content.split("\n");
    let i = 1;
    for (const line of lines) {
      if (line.trim().match(/^[-*]\s+/)) {
        testCases.push({
          testNr: `TC-${String(i++).padStart(3, "0")}`,
          testinhalt: line.replace(/^[-*]\s+/, "").substring(0, 50),
          beschreibung: line,
          resultat: "",
          testdatum: "",
          buildId: "",
          tester: "",
          kommentar: "",
        });
      }
    }
  }
  return testCases;
}

function processPlanContent(plan: TestPlan): ProcessedTestPlan {
  try {
    // Try parsing as structured JSON
    const json: GenerationStatus = JSON.parse(plan.content);

    // Check if it looks like our status object
    if (json.status) {
      let cases: TestCase[] = [];

      // Handle both v1 and v2 formats
      const planData = json.data || json;
      
      // Map structured cases to UI format
      if (planData.test_cases) {
        cases = planData.test_cases.map((tc: any) => ({
          testNr: tc.test_id,
          testinhalt: tc.title,
          beschreibung: tc.description,
          vorbedingung: tc.preconditions || "",
          schritte: tc.steps || "",
          erwartetes_ergebnis: tc.expected_result || "",
          resultat: "",
          testdatum: "",
          buildId: "",
          tester: "",
          kommentar: "",
        }));
      }

      return {
        ...plan,
        isStructured: true,
        status: json.status,
        generationState: {
          ...json,
          data: planData, // Ensure data is accessible
        },
        testCases: cases,
      };
    }
  } catch (e) {
    // Not JSON, fall back to Markdown
    console.debug("Plan is not structured JSON, using Markdown parser", e);
  }

  return {
    ...plan,
    isStructured: false,
    status: "completed",
    testCases: parseTestCases(plan.content),
  };
}

export default function ProjectPage() {
  const params = useParams();
  const id = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [testPlans, setTestPlans] = useState<ProcessedTestPlan[]>([]);

  // UI State
  const [isUploading, setIsUploading] = useState<"ddd" | "context" | null>(
    null,
  );
  const [isGenerating, setIsGenerating] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStage, setUploadStage] = useState<
    "uploading" | "processing" | "done"
  >("uploading");

  // Viewer State
  const [viewerOpen, setViewerOpen] = useState(false);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);

  // Document Selection State
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [showDocSelector, setShowDocSelector] = useState(false);

  // New: Tab-based UI for Testplan vs Chat
  const [activeTab, setActiveTab] = useState<"testplan" | "chat">("testplan");

  // New: Collapsible sidebar
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Test Execution State
  const [filterStatus, setFilterStatus] = useState<string | null>(null);
  const [filterPriority, setFilterPriority] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTests, setSelectedTests] = useState<Set<string>>(new Set());
  const [bulkStatus, setBulkStatus] = useState<"passed" | "failed" | "skipped" | "pending" | null>(null);

  // Test Execution Hooks
  const activePlanId = testPlans.length > 0 ? testPlans[0].id : null;
  const { data: testExecutions = [] } = useTestExecutions(id, activePlanId || "");
  const { data: testStatistics } = useTestStatistics(id, activePlanId || "");
  const saveExecutionMutation = useSaveTestExecution(id, activePlanId || "");
  const bulkSaveMutation = useBulkSaveTestExecutions(id, activePlanId || "");

  const loadData = useCallback(async () => {
    try {
      const [projRes, docsRes, plansRes] = await Promise.all([
        fetch(`${API_URL}/api/testing/projects/${id}`),
        fetch(`${API_URL}/api/testing/projects/${id}/documents`),
        fetch(`${API_URL}/api/testing/projects/${id}/plans`),
      ]);

      if (projRes.ok) setProject(await projRes.json());
      if (docsRes.ok) setDocuments(await docsRes.json());
      if (plansRes.ok) {
        const plans = await plansRes.json();
        const processed = plans.map(processPlanContent);
        setTestPlans(processed);

        // Polling logic if any plan is processing
        const hasProcessing = processed.some(
          (p: ProcessedTestPlan) => p.status === "processing",
        );
        if (hasProcessing) {
          setIsGenerating(true); // Keep spinner active
          setTimeout(loadData, 2000); // Poll again
        } else {
          setIsGenerating(false);
        }
      }
    } catch (error) {
      console.error("Failed to load project data:", error);
    }
  }, [id]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleUpload = async (
    event: React.ChangeEvent<HTMLInputElement>,
    category: "ddd" | "context",
  ) => {
    if (!event.target.files?.length) return;

    setIsUploading(category);
    setUploadProgress(0);
    setUploadStage("uploading");

    const file = event.target.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Use XMLHttpRequest for progress tracking
      const xhr = new XMLHttpRequest();

      const uploadPromise = new Promise<{ task_id?: string }>(
        (resolve, reject) => {
          xhr.upload.addEventListener("progress", (e) => {
            if (e.lengthComputable) {
              const percent = Math.round((e.loaded / e.total) * 100);
              setUploadProgress(percent);
            }
          });

          xhr.addEventListener("load", () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              try {
                resolve(JSON.parse(xhr.responseText));
              } catch {
                resolve({});
              }
            } else {
              reject(new Error("Upload failed"));
            }
          });

          xhr.addEventListener("error", () =>
            reject(new Error("Upload failed")),
          );

          xhr.open(
            "POST",
            `${API_URL}/api/testing/projects/${id}/documents?category=${category}`,
          );
          xhr.withCredentials = true; // Enable cookie-based auth
          xhr.send(formData);
        },
      );


      const data = await uploadPromise;

      // Switch to processing stage
      setUploadStage("processing");
      setUploadProgress(100);

      // Immediately load to show document with filename
      loadData();

      // Poll for processing completion if task_id returned
      if (data.task_id) {
        const pollInterval = setInterval(async () => {
          const docsRes = await fetch(
            `${API_URL}/api/testing/projects/${id}/documents`,
          );
          if (docsRes.ok) {
            const docs = await docsRes.json();
            const uploadedDoc = docs.find(
              (d: Document) => d.doc_id === data.task_id,
            );
            if (uploadedDoc?.processing_status === "completed") {
              clearInterval(pollInterval);
              setUploadStage("done");

              // Auto-generate description if it was a DDD upload
              if (category === "ddd") {
                try {
                  const descRes = await fetch(
                    `${API_URL}/api/testing/projects/${id}/generate-description`,
                    {
                      method: "POST",
                    },
                  );
                  if (descRes.ok) {
                    const descData = await descRes.json();
                    if (descData.description) {
                      // Update project with generated description
                      await fetch(`${API_URL}/api/testing/projects/${id}`, {
                        method: "PATCH",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                          description: descData.description,
                        }),
                      });
                    }
                  }
                } catch (e) {
                  console.error("Auto-description generation failed:", e);
                }
              }

              setTimeout(() => {
                setIsUploading(null);
                setUploadProgress(0);
              }, 800);
              loadData();
            } else if (uploadedDoc?.processing_status === "failed") {
              clearInterval(pollInterval);
              setIsUploading(null);
              setUploadProgress(0);
              loadData();
            }
          }
        }, 1500);

        // Stop polling after 60 seconds
        setTimeout(() => {
          clearInterval(pollInterval);
          setIsUploading(null);
          setUploadProgress(0);
        }, 60000);
      } else {
        // No task_id, assume immediate completion
        setUploadStage("done");
        setTimeout(() => {
          setIsUploading(null);
          setUploadProgress(0);
        }, 800);
      }
    } catch (error) {
      console.error("Upload failed:", error);
      setIsUploading(null);
      setUploadProgress(0);
    }

    // Reset file input
    event.target.value = "";
  };

  const generatePlan = async () => {
    setIsGenerating(true);
    try {
      // Build request with document selection support
      const requestBody: {
        selected_doc_ids?: string[];
      } = {};

      if (selectedDocIds.length > 0) {
        // Explicit document selection
        requestBody.selected_doc_ids = selectedDocIds;
      }
      // If empty, use all documents (no filter)

      await fetch(`${API_URL}/api/testing/projects/${id}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });
      loadData();
    } catch (error) {
      console.error("Generation failed:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  // Toggle RAG enabled status for a document
  const toggleRAG = async (docId: string, currentStatus: boolean) => {
    try {
      const response = await fetch(
        `${API_URL}/api/testing/projects/${id}/documents/${docId}/rag`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ rag_enabled: !currentStatus }),
        },
      );

      if (response.ok) {
        // Update local state optimistically
        setDocuments((docs) =>
          docs.map((d) =>
            d.doc_id === docId ? { ...d, rag_enabled: !currentStatus } : d,
          ),
        );
      } else {
        console.error("Failed to toggle RAG status");
      }
    } catch (error) {
      console.error("Toggle RAG error:", error);
    }
  };

  // Delete confirmation modal state
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteDocTarget, setDeleteDocTarget] = useState<{
    docId: string;
    filename: string;
  } | null>(null);

  // Show delete confirmation
  const confirmDeleteDocument = (
    docId: string,
    filename: string,
    event: React.MouseEvent,
  ) => {
    event.stopPropagation();
    event.preventDefault();
    setDeleteDocTarget({ docId, filename });
    setShowDeleteModal(true);
  };

  // Execute delete
  const executeDeleteDocument = async () => {
    if (!deleteDocTarget) return;
    try {
      const response = await fetch(
        `${API_URL}/api/testing/projects/${id}/documents/${deleteDocTarget.docId}`,
        {
          method: "DELETE",
        },
      );

      if (response.ok) {
        loadData(); // Refresh document list
      } else {
        console.error("Delete failed");
      }
    } catch (error) {
      console.error("Delete error:", error);
    } finally {
      setShowDeleteModal(false);
      setDeleteDocTarget(null);
    }
  };

  const exportToExcel = async (plan: TestPlan) => {
    const testCases = plan.testCases || parseTestCases(plan.content);

    // Create workbook and worksheet
    const workbook = new ExcelJS.Workbook();
    workbook.creator = "Streamworks";
    workbook.created = new Date();

    const worksheet = workbook.addWorksheet("Testplan");

    // Define columns with German headers
    worksheet.columns = [
      { header: "Testnr.", key: "testNr", width: 10 },
      { header: "Testinhalt", key: "testinhalt", width: 30 },
      { header: "Testbeschreibung", key: "beschreibung", width: 40 },
      { header: "Vorbedingung", key: "vorbedingung", width: 30 },
      { header: "Schritte", key: "schritte", width: 40 },
      { header: "Erwartetes Ergebnis", key: "erwartetes_ergebnis", width: 30 },
      { header: "Resultat", key: "resultat", width: 12 },
      { header: "Testdatum", key: "testdatum", width: 12 },
      { header: "Build ID", key: "buildId", width: 12 },
      { header: "Tester", key: "tester", width: 15 },
      { header: "Kommentar", key: "kommentar", width: 20 },
    ];

    // Style header row
    const headerRow = worksheet.getRow(1);
    headerRow.font = { bold: true };
    headerRow.fill = {
      type: "pattern",
      pattern: "solid",
      fgColor: { argb: "FFE0E7FF" }, // Light indigo
    };

    // Add data rows
    testCases.forEach((tc) => {
      worksheet.addRow({
        testNr: tc.testNr,
        testinhalt: tc.testinhalt,
        beschreibung: tc.beschreibung,
        vorbedingung: (tc as any).vorbedingung || "",
        schritte: (tc as any).schritte || "",
        erwartetes_ergebnis: (tc as any).erwartetes_ergebnis || "",
        resultat: tc.resultat,
        testdatum: tc.testdatum,
        buildId: tc.buildId,
        tester: tc.tester,
        kommentar: tc.kommentar,
      });
    });

    // Generate buffer and save
    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    const safeName = (project?.name || "Export").replace(/[^a-z0-9]/gi, "_");
    const filename = `Testplan_${safeName}_${new Date().toISOString().split("T")[0]}.xlsx`;

    saveAs(blob, filename);
  };

  const openDocument = (docId: string) => {
    setSelectedDocId(docId);
    setViewerOpen(true);
  };

  // --- Interaction Logic ---
  const [selectedTestCase, setSelectedTestCase] = useState<TestCase | null>(
    null,
  );
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  const handleAddTestCase = (plan: ProcessedTestPlan) => {
    const nextNum = (plan.testCases?.length || 0) + 1;
    const newCase: TestCase = {
      testNr: `TC-MAN-${String(nextNum).padStart(3, "0")}`,
      testinhalt: "Neuer Testfall",
      beschreibung: "",
      resultat: "",
      testdatum: "",
      buildId: "",
      tester: "",
      kommentar: "",
      // Additional fields hacked in for now
      vorbedingung: "",
      schritte: "",
      erwartetes_ergebnis: "",
    };
    setSelectedTestCase(newCase);
    setIsEditing(true);
    setShowDetailModal(true);
  };

  const saveTestCaseChanges = async () => {
    if (!selectedTestCase || testPlans.length === 0) return;

    // 1. Update local state
    const activePlanIndex = 0; // MVP: Assume first plan
    const originalPlan = testPlans[activePlanIndex];

    // Check if exists
    const exists = originalPlan.testCases.some(
      (tc) => tc.testNr === selectedTestCase.testNr,
    );

    let newCases;
    if (exists) {
      newCases = originalPlan.testCases.map((tc) =>
        tc.testNr === selectedTestCase.testNr ? selectedTestCase : tc,
      );
    } else {
      newCases = [selectedTestCase, ...originalPlan.testCases];
    }

    // Update local plan immediately
    const updatedPlan = { ...originalPlan, testCases: newCases };
    const newPlans = [...testPlans];
    newPlans[activePlanIndex] = updatedPlan;
    setTestPlans(newPlans);

    // 2. Persist to Backend
    // Reconstruct full JSON structure if it was structured
    let contentToSave = "";
    if (originalPlan.isStructured && originalPlan.generationState) {
      const newState = {
        ...originalPlan.generationState,
        data: {
          ...originalPlan.generationState.data,
          test_cases: newCases.map((tc) => ({
            test_id: tc.testNr,
            title: tc.testinhalt,
            description: tc.beschreibung,
            preconditions: (tc as any).vorbedingung || "",
            steps: (tc as any).schritte || "",
            expected_result: (tc as any).erwartetes_ergebnis || "",
          })),
        },
      };
      // Wrap in status object
      contentToSave = JSON.stringify({
        status: originalPlan.status,
        format: "structured_v1",
        data: newState.data,
      });
    } else {
      // Can't easily save back to MD yet without a parser-writer, warn user or handle text append
      // For now, we will just not save to DB for legacy plans to avoid corruption
      // Or ideally, we convert to the new JSON structure!
      const newState = {
        test_cases: newCases.map((tc) => ({
          test_id: tc.testNr,
          title: tc.testinhalt,
          description: tc.beschreibung,
          preconditions: (tc as any).vorbedingung || "",
          steps: (tc as any).schritte || "",
          expected_result: (tc as any).erwartetes_ergebnis || "",
        })),
        introduction: "Converted from legacy",
        summary: "",
      };
      contentToSave = JSON.stringify({
        status: "completed",
        format: "structured_v1",
        data: newState,
      });
    }

    try {
      await fetch(
        `${API_URL}/api/testing/projects/${id}/plans/${originalPlan.id}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content: contentToSave }),
        },
      );
    } catch (e) {
      console.error("Failed to save plan", e);
      // Revert on error?
    }

    setIsEditing(false);
    setShowDetailModal(false);
  };

  // Filter documents
  const dddDocs = documents.filter((d) => d.metadata?.category === "ddd");
  const contextDocs = documents.filter((d) => d.metadata?.category !== "ddd");

  // Check if any DDD documents are still processing
  const hasProcessingDdds = dddDocs.some(
    (d) => d.processing_status && d.processing_status !== "completed",
  );
  const canGenerate = dddDocs.length > 0 && !hasProcessingDdds;

  if (!project)
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      </AppLayout>
    );

  return (
    <AppLayout>
      <div className="flex flex-col h-full gap-4">
        {/* Header - Premium Design with Stats */}
        <div className="relative flex-shrink-0 pb-4">
          {/* Background decoration */}
          <div className="absolute -top-16 -left-16 w-56 h-56 bg-gradient-to-br from-blue-100/30 to-teal-100/30 rounded-full blur-3xl pointer-events-none" />

          <div className="relative flex items-start justify-between">
            <div className="flex items-start gap-4">
              {/* Gradient Icon */}
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="p-3 bg-gradient-to-br from-[var(--arvato-blue)] to-[#00D4AA] rounded-xl shadow-lg shadow-blue-500/20 flex-shrink-0"
              >
                <Beaker className="w-6 h-6 text-white" />
              </motion.div>

              <div className="max-w-xl">
                <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
                  <span className="hover:text-[var(--arvato-blue)] cursor-pointer transition-colors">Testing</span>
                  <span>/</span>
                  <span className="text-slate-600 font-medium">{project.name}</span>
                </div>
                <h1 className="text-xl font-bold text-slate-800">
                  {project.name}
                </h1>
                {project.description && (
                  <p className="text-sm text-slate-500 mt-1 line-clamp-2">
                    {project.description}
                  </p>
                )}
              </div>
            </div>

            {/* Actions Group */}
            <div className="flex items-center gap-3">
              {/* Stats Badges */}
              <div className="hidden lg:flex items-center gap-2 mr-2">
                <div className="stat-card !py-2 !px-3 flex items-center gap-2">
                  <FileText className="w-3.5 h-3.5 text-[var(--arvato-blue)]" />
                  <span className="text-sm font-bold text-slate-700">{documents.length}</span>
                  <span className="text-xs text-slate-500">Docs</span>
                </div>
                {testPlans.length > 0 && testPlans[0]?.testCases?.length > 0 && (
                  <div className="stat-card !py-2 !px-3 flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-emerald-500" />
                    <span className="text-sm font-bold text-slate-700">{testPlans[0].testCases.length}</span>
                    <span className="text-xs text-slate-500">Tests</span>
                  </div>
                )}
              </div>

              {/* Excel Export Button */}
              {testPlans.length > 0 && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => exportToExcel(testPlans[0])}
                  className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 hover:border-slate-300 rounded-xl text-sm font-medium transition-all shadow-sm"
                  title="Als Excel exportieren"
                >
                  <Download className="w-4 h-4" />
                  Export
                </motion.button>
              )}

              {/* Generate Button - Premium */}
              <motion.button
                whileHover={canGenerate && !isGenerating ? { scale: 1.02 } : {}}
                whileTap={canGenerate && !isGenerating ? { scale: 0.98 } : {}}
                onClick={generatePlan}
                disabled={isGenerating || !canGenerate}
                className={`
                  flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all
                  ${!canGenerate
                    ? "bg-slate-100 text-slate-400 cursor-not-allowed"
                    : isGenerating
                      ? "bg-gradient-to-r from-blue-100 to-teal-100 text-[var(--arvato-blue)]"
                      : "bg-gradient-to-r from-[var(--arvato-blue)] to-[var(--arvato-blue-dark)] text-white shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/30"
                  }
                `}
              >
                {isGenerating ? (
                  <>
                    <span className="w-4 h-4 border-2 border-[var(--arvato-blue)] border-t-transparent rounded-full animate-spin" />
                    Generiere...
                  </>
                ) : (
                  <>
                    <Cpu className="w-4 h-4" />
                    Testplan generieren
                  </>
                )}
              </motion.button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex gap-4 overflow-hidden">
          {/* Left Sidebar: Collapsible Projektdokumente */}
          <div
            className={`flex-shrink-0 transition-all duration-300 ${sidebarCollapsed ? "w-10" : "w-72"} flex flex-col`}
          >
            {sidebarCollapsed ? (
              /* Collapsed State - vertical strip */
              <div className="h-full glass-card rounded-xl flex flex-col items-center pt-3 shadow-premium">
                <button
                  onClick={() => setSidebarCollapsed(false)}
                  className="p-2 hover:bg-[var(--arvato-blue)]/10 rounded-lg transition-colors"
                  title="Sidebar einblenden"
                >
                  <ChevronRight className="w-4 h-4 text-[var(--arvato-blue)]" />
                </button>
                <div className="mt-2 flex flex-col items-center gap-2">
                  <FolderOpen className="w-4 h-4 text-[var(--arvato-blue)]" />
                  <span
                    className="text-xs text-slate-500 font-medium writing-mode-vertical-lr rotate-180"
                    style={{ writingMode: "vertical-rl" }}
                  >
                    {dddDocs.length + contextDocs.length} Dokumente
                  </span>
                </div>
              </div>
            ) : (
              /* Expanded State - full sidebar with glassmorphism */
              <div className="h-full glass-card rounded-xl flex flex-col overflow-hidden shadow-premium">
                {/* Header with gradient accent */}
                <div className="relative flex items-center justify-between p-3 border-b border-slate-100/50">
                  <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-[var(--arvato-blue)] to-[#00D4AA]" />
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-gradient-to-br from-[var(--arvato-blue)]/10 to-[#00D4AA]/10 rounded-lg">
                      <FolderOpen className="w-4 h-4 text-[var(--arvato-blue)]" />
                    </div>
                    <span className="text-sm font-semibold text-slate-700">
                      Projektdokumente
                    </span>
                    <span className="badge-glass !text-xs !py-0.5">
                      {dddDocs.length + contextDocs.length}
                    </span>
                  </div>
                  <button
                    onClick={() => setSidebarCollapsed(true)}
                    className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors"
                    title="Sidebar einklappen"
                  >
                    <ChevronLeft className="w-4 h-4 text-slate-400" />
                  </button>
                </div>

                {/* Scrollable content */}
                <div className="flex-1 overflow-y-auto p-3 space-y-3">
                  {/* DDD Subsection */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-[var(--arvato-blue)] uppercase tracking-wider flex items-center gap-1.5">
                        <FileText className="w-3 h-3" />
                        DDD (PDF/MD)
                      </span>
                      {dddDocs.length === 0 && !isUploading && (
                        <label className="text-xs text-indigo-600 hover:text-indigo-700 cursor-pointer font-medium">
                          <input
                            type="file"
                            className="hidden"
                            onChange={(e) => handleUpload(e, "ddd")}
                            accept=".pdf,.md,.markdown"
                          />
                          + Hochladen
                        </label>
                      )}
                    </div>

                    {/* Upload Progress */}
                    {isUploading === "ddd" && (
                      <div className="mb-2 p-2 bg-indigo-50 rounded-lg">
                        <div className="flex items-center gap-2">
                          {uploadStage === "done" ? (
                            <CheckCircle className="w-3.5 h-3.5 text-green-500" />
                          ) : (
                            <span className="w-3.5 h-3.5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin flex-shrink-0" />
                          )}
                          <span className="text-xs text-indigo-700">
                            {uploadStage === "uploading" && "Hochladen..."}
                            {uploadStage === "processing" && "Verarbeite..."}
                            {uploadStage === "done" && "Fertig!"}
                          </span>
                          <span className="text-xs text-indigo-500 ml-auto">
                            {uploadProgress}%
                          </span>
                        </div>
                        <div className="w-full bg-indigo-200 rounded-full h-1.5 mt-1.5">
                          <div
                            className={`h-full transition-all duration-300 rounded-full ${uploadStage === "done" ? "bg-green-500" : "bg-indigo-600"}`}
                            style={{ width: `${uploadProgress}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {dddDocs.length > 0 ? (
                      <div className="space-y-1">
                        {dddDocs.map((doc) => {
                          const isProcessing =
                            doc.processing_status &&
                            doc.processing_status !== "completed";
                          return (
                            <div
                              key={doc.doc_id}
                              onClick={() =>
                                !isProcessing && openDocument(doc.doc_id)
                              }
                              className={`flex items-center gap-2 p-2 rounded-md transition-colors group ${isProcessing
                                ? "bg-amber-50 cursor-wait"
                                : "bg-indigo-50 cursor-pointer hover:bg-indigo-100"
                                }`}
                            >
                              {isProcessing ? (
                                <span className="w-3.5 h-3.5 border-2 border-amber-500 border-t-transparent rounded-full animate-spin flex-shrink-0" />
                              ) : (
                                <FileText className="w-3.5 h-3.5 text-indigo-600 flex-shrink-0" />
                              )}
                              <span
                                className={`text-xs truncate flex-1 ${isProcessing ? "text-amber-700" : "text-slate-700"}`}
                              >
                                {doc.metadata.filename}
                              </span>
                              {!isProcessing && (
                                <>
                                  {/* RAG Toggle */}
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      toggleRAG(
                                        doc.doc_id,
                                        doc.rag_enabled !== false,
                                      );
                                    }}
                                    className={`p-0.5 rounded transition-all ${doc.rag_enabled === false
                                      ? "bg-slate-100 text-slate-400"
                                      : "bg-indigo-100 text-indigo-600"
                                      }`}
                                    title={
                                      doc.rag_enabled === false
                                        ? "RAG deaktiviert"
                                        : "RAG aktiviert"
                                    }
                                  >
                                    <Database className="w-3 h-3" />
                                  </button>
                                  <button
                                    onClick={(e) =>
                                      confirmDeleteDocument(
                                        doc.doc_id,
                                        doc.metadata.filename,
                                        e,
                                      )
                                    }
                                    className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-red-100 rounded transition-all"
                                  >
                                    <Trash2 className="w-3 h-3 text-red-500" />
                                  </button>
                                </>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      !isUploading && (
                        <div className="text-xs text-slate-400 py-1 pl-1">
                          —
                        </div>
                      )
                    )}
                  </div>

                  {/* Context Subsection */}
                  <div className="pt-2 border-t border-slate-100">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-slate-500 uppercase tracking-wide flex items-center gap-1.5">
                        <FileText className="w-3 h-3" />
                        Kontext
                      </span>
                      <label
                        className={`text-xs text-slate-500 hover:text-slate-700 cursor-pointer ${isUploading === "context" ? "opacity-50 pointer-events-none" : ""}`}
                      >
                        <input
                          type="file"
                          className="hidden"
                          onChange={(e) => handleUpload(e, "context")}
                          multiple
                        />
                        {isUploading === "context" ? (
                          "..."
                        ) : (
                          <Plus className="w-3.5 h-3.5" />
                        )}
                      </label>
                    </div>

                    {contextDocs.length > 0 ? (
                      <div className="space-y-1">
                        {contextDocs.map((doc) => (
                          <div
                            key={doc.doc_id}
                            onClick={() => openDocument(doc.doc_id)}
                            className="flex items-center gap-2 py-1 text-xs text-slate-600 hover:text-slate-800 cursor-pointer group"
                          >
                            <FileText className="w-3 h-3 text-slate-400" />
                            <span className="truncate flex-1">
                              {doc.metadata.filename}
                            </span>
                            {/* RAG Toggle */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleRAG(
                                  doc.doc_id,
                                  doc.rag_enabled !== false,
                                );
                              }}
                              className={`p-0.5 rounded transition-all ${doc.rag_enabled === false
                                ? "bg-slate-100 text-slate-400"
                                : "bg-indigo-100 text-indigo-600"
                                }`}
                              title={
                                doc.rag_enabled === false
                                  ? "RAG deaktiviert"
                                  : "RAG aktiviert"
                              }
                            >
                              <Database className="w-3 h-3" />
                            </button>
                            <button
                              onClick={(e) =>
                                confirmDeleteDocument(
                                  doc.doc_id,
                                  doc.metadata.filename,
                                  e,
                                )
                              }
                              className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-red-100 rounded transition-all"
                            >
                              <Trash2 className="w-3 h-3 text-red-500" />
                            </button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-xs text-slate-400 py-1 pl-1">—</div>
                    )}
                  </div>

                  {/* Document Selection Subsection */}
                  <div className="pt-2 border-t border-slate-100">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-slate-500 uppercase tracking-wide flex items-center gap-1.5">
                        <Database className="w-3 h-3" />
                        RAG-Kontext
                      </span>
                    </div>

                    <button
                      onClick={() => setShowDocSelector(true)}
                      className="w-full flex items-center justify-between px-2 py-1.5 bg-slate-50 hover:bg-slate-100 rounded-lg border border-slate-200 transition-all group text-xs"
                    >
                      <span className="text-slate-600">
                        {selectedDocIds.length === 0
                          ? "Alle Dokumente"
                          : `${selectedDocIds.length} ausgewählt`}
                      </span>
                      <span className="text-slate-400 group-hover:text-slate-600">
                        →
                      </span>
                    </button>

                    {selectedDocIds.length > 0 && (
                      <button
                        onClick={() => setSelectedDocIds([])}
                        className="mt-1 text-xs text-indigo-600 hover:text-indigo-800"
                      >
                        Zurücksetzen
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Tabs for Testplan and Chat */}
          <div className="flex-1 flex flex-col overflow-hidden glass-card rounded-xl shadow-premium">
            {/* Tab Header - Premium Pill Style */}
            <div className="px-5 py-3 border-b border-slate-100/50 flex items-center justify-between">
              <div className="flex items-center gap-1 p-1 bg-slate-100/50 rounded-xl">
                <button
                  onClick={() => setActiveTab("testplan")}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${activeTab === "testplan"
                    ? "bg-white text-[var(--arvato-blue)] shadow-sm"
                    : "text-slate-500 hover:text-slate-700"
                    }`}
                >
                  <span className="flex items-center gap-2">
                    📋 Testplan
                    {testPlans.length > 0 &&
                      testPlans[0]?.testCases?.length > 0 && (
                        <span className="badge-gradient !text-[10px] !px-2 !py-0.5">
                          {testPlans[0].testCases.length}
                        </span>
                      )}
                  </span>
                </button>
                <button
                  onClick={() => setActiveTab("chat")}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${activeTab === "chat"
                    ? "bg-white text-[var(--arvato-blue)] shadow-sm"
                    : "text-slate-500 hover:text-slate-700"
                    }`}
                >
                  💬 DDD Chat
                </button>
              </div>

              {/* Context actions for testplan tab */}
              {activeTab === "testplan" && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleAddTestCase(testPlans[0])}
                  disabled={testPlans.length === 0}
                  className="px-3 py-1.5 text-xs font-medium bg-gradient-to-r from-[var(--arvato-blue)]/10 to-[#00D4AA]/10 hover:from-[var(--arvato-blue)]/20 hover:to-[#00D4AA]/20 text-[var(--arvato-blue)] rounded-lg flex items-center gap-1.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed border border-[var(--arvato-blue)]/20"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Testfall
                </motion.button>
              )}
            </div>

            {/* Tab Content */}
            <div className="flex-1 overflow-y-auto">
              {activeTab === "testplan" ? (
                /* Testplan Content */
                testPlans.length > 0 ? (
                  <div className="divide-y divide-slate-100">
                    {testPlans.map((plan) => (
                      <div key={plan.id} className="p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2 text-xs text-slate-500">
                            <CheckCircle className="w-3.5 h-3.5 text-green-500" />
                            <Clock className="w-3 h-3" />
                            {new Date(plan.created_at).toLocaleString("de-DE")}
                            {plan.testCases && plan.testCases.length > 0 && (
                              <span className="ml-2 px-2 py-0.5 bg-slate-100 rounded text-slate-600">
                                {plan.testCases.length} Tests
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => exportToExcel(plan)}
                              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-50 rounded-md transition-colors"
                              title="Als Excel exportieren"
                            >
                              <Download className="w-3.5 h-3.5" />
                              Excel
                            </button>
                            <button
                              onClick={async () => {
                                if (confirm("Möchten Sie diesen Testplan wirklich löschen? Alle zugehörigen Test-Ergebnisse werden ebenfalls gelöscht.")) {
                                  try {
                                    const response = await fetch(
                                      `${API_URL}/api/testing/projects/${id}/plans/${plan.id}`,
                                      { method: "DELETE" }
                                    );
                                    if (response.ok) {
                                      loadData();
                                    } else {
                                      alert("Fehler beim Löschen des Testplans");
                                    }
                                  } catch (error) {
                                    console.error("Delete plan error:", error);
                                    alert("Fehler beim Löschen des Testplans");
                                  }
                                }
                              }}
                              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
                              title="Testplan löschen"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                              Löschen
                            </button>
                          </div>
                        </div>

                        {/* Progress Status or Table */}
                        {plan.status === "processing" &&
                          plan.generationState ? (
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mb-4 bg-gradient-to-r from-blue-50 via-teal-50/50 to-blue-50 border border-blue-100/50 rounded-xl p-5"
                          >
                            <div className="flex items-center gap-3 mb-3">
                              <div className="relative w-6 h-6">
                                <div className="absolute inset-0 rounded-full border-2 border-[var(--arvato-blue)]/20" />
                                <div className="absolute inset-0 rounded-full border-2 border-[var(--arvato-blue)] border-t-transparent animate-spin" />
                              </div>
                              <h4 className="font-semibold text-slate-800">
                                Testplan wird generiert...
                              </h4>
                            </div>
                            <p className="text-sm text-slate-600 mb-4 ml-9">
                              {plan.generationState.message ||
                                "Einen Moment bitte..."}
                            </p>
                            <div className="ml-9 max-w-sm">
                              <div className="progress-premium">
                                <div
                                  className="progress-premium-fill"
                                  style={{
                                    width: `${plan.generationState.progress || 0}%`,
                                  }}
                                />
                              </div>
                              <p className="text-xs text-slate-500 mt-2">{plan.generationState.progress || 0}% abgeschlossen</p>
                            </div>
                          </motion.div>
                        ) : plan.status === "failed" ? (
                          <div className="mb-4 bg-red-50 border border-red-100 rounded-lg p-4 text-red-800 text-sm">
                            <strong>Fehler bei der Generierung:</strong>
                            <br />
                            {plan.generationState?.error ||
                              "Unbekannter Fehler"}
                          </div>
                        ) : (
                          /* Completed Plan Table with Enhanced Features */
                          plan.testCases &&
                          plan.testCases.length > 0 && (
                            <div className="mb-4 space-y-4">
                              {/* Statistics Dashboard */}
                              {testStatistics && (
                                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                                  <div className="stat-card !p-3">
                                    <div className="flex items-center gap-2 mb-1">
                                      <BarChart3 className="w-4 h-4 text-[var(--arvato-blue)]" />
                                      <span className="text-xs text-slate-500">Gesamt</span>
                                    </div>
                                    <p className="text-xl font-bold text-slate-800">{testStatistics.total}</p>
                                  </div>
                                  <div className="stat-card !p-3 bg-emerald-50/50 border-emerald-100">
                                    <div className="flex items-center gap-2 mb-1">
                                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                                      <span className="text-xs text-slate-500">Bestanden</span>
                                    </div>
                                    <p className="text-xl font-bold text-emerald-700">{testStatistics.passed}</p>
                                  </div>
                                  <div className="stat-card !p-3 bg-red-50/50 border-red-100">
                                    <div className="flex items-center gap-2 mb-1">
                                      <XCircle className="w-4 h-4 text-red-600" />
                                      <span className="text-xs text-slate-500">Fehlgeschlagen</span>
                                    </div>
                                    <p className="text-xl font-bold text-red-700">{testStatistics.failed}</p>
                                  </div>
                                  <div className="stat-card !p-3 bg-amber-50/50 border-amber-100">
                                    <div className="flex items-center gap-2 mb-1">
                                      <SkipForward className="w-4 h-4 text-amber-600" />
                                      <span className="text-xs text-slate-500">Übersprungen</span>
                                    </div>
                                    <p className="text-xl font-bold text-amber-700">{testStatistics.skipped}</p>
                                  </div>
                                  <div className="stat-card !p-3 bg-blue-50/50 border-blue-100">
                                    <div className="flex items-center gap-2 mb-1">
                                      <TrendingUp className="w-4 h-4 text-blue-600" />
                                      <span className="text-xs text-slate-500">Pass Rate</span>
                                    </div>
                                    <p className="text-xl font-bold text-blue-700">{testStatistics.pass_rate}%</p>
                                  </div>
                                </div>
                              )}

                              {/* Filters and Search */}
                              <div className="flex flex-wrap items-center gap-3 p-3 bg-slate-50/50 rounded-xl border border-slate-200/50">
                                <div className="flex items-center gap-2 flex-1 min-w-[200px]">
                                  <Search className="w-4 h-4 text-slate-400" />
                                  <input
                                    type="text"
                                    placeholder="Testfälle suchen..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="flex-1 text-xs px-3 py-1.5 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--arvato-blue)]/20 focus:border-[var(--arvato-blue)]"
                                  />
                                </div>
                                <select
                                  value={filterStatus || ""}
                                  onChange={(e) => setFilterStatus(e.target.value || null)}
                                  className="text-xs px-3 py-1.5 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--arvato-blue)]/20"
                                >
                                  <option value="">Alle Status</option>
                                  <option value="passed">Bestanden</option>
                                  <option value="failed">Fehlgeschlagen</option>
                                  <option value="skipped">Übersprungen</option>
                                  <option value="pending">Ausstehend</option>
                                </select>
                                {selectedTests.size > 0 && (
                                  <div className="flex items-center gap-2">
                                    <span className="text-xs text-slate-600">{selectedTests.size} ausgewählt</span>
                                    <select
                                      value={bulkStatus || ""}
                                      onChange={(e) => {
                                        const status = e.target.value as any;
                                        if (status) {
                                          setBulkStatus(status);
                                          const executions: TestExecutionRequest[] = Array.from(selectedTests).map(
                                            (testId) => ({
                                              test_id: testId,
                                              status: status,
                                            })
                                          );
                                          bulkSaveMutation.mutate(executions);
                                          setSelectedTests(new Set());
                                          setBulkStatus(null);
                                        }
                                      }}
                                      className="text-xs px-3 py-1.5 bg-white border border-slate-200 rounded-lg focus:outline-none"
                                    >
                                      <option value="">Bulk-Status...</option>
                                      <option value="passed">✓ Bestanden</option>
                                      <option value="failed">✗ Fehlgeschlagen</option>
                                      <option value="skipped">⊘ Übersprungen</option>
                                      <option value="pending">⏳ Ausstehend</option>
                                    </select>
                                    <button
                                      onClick={() => setSelectedTests(new Set())}
                                      className="text-xs text-slate-500 hover:text-slate-700"
                                    >
                                      Abbrechen
                                    </button>
                                  </div>
                                )}
                              </div>

                              {/* Enhanced Table */}
                              <div className="border border-slate-200/50 rounded-xl overflow-hidden shadow-sm">
                                <table className="w-full text-xs">
                                  <thead className="bg-gradient-to-r from-slate-50 to-slate-100/50">
                                    <tr>
                                      <th className="px-3 py-3 w-8">
                                        <input
                                          type="checkbox"
                                          checked={selectedTests.size === plan.testCases.length && plan.testCases.length > 0}
                                          onChange={(e) => {
                                            if (e.target.checked) {
                                              setSelectedTests(new Set(plan.testCases.map((tc) => tc.testNr)));
                                            } else {
                                              setSelectedTests(new Set());
                                            }
                                          }}
                                          className="rounded border-slate-300 text-[var(--arvato-blue)] focus:ring-[var(--arvato-blue)]"
                                        />
                                      </th>
                                      <th className="px-4 py-3 text-left font-semibold text-slate-600">Nr.</th>
                                      <th className="px-4 py-3 text-left font-semibold text-slate-600">Status</th>
                                      <th className="px-4 py-3 text-left font-semibold text-slate-600">Testinhalt</th>
                                      <th className="px-4 py-3 text-left font-semibold text-slate-600">Beschreibung</th>
                                      <th className="px-4 py-3 text-right font-semibold text-slate-600 w-24">Aktion</th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-slate-100/50">
                                    {plan.testCases
                                      .filter((tc) => {
                                        if (filterStatus) {
                                          const execution = testExecutions.find((e) => e.test_id === tc.testNr);
                                          const status = execution?.status || "pending";
                                          if (status !== filterStatus) return false;
                                        }
                                        if (searchQuery) {
                                          const query = searchQuery.toLowerCase();
                                          if (
                                            !tc.testNr.toLowerCase().includes(query) &&
                                            !tc.testinhalt.toLowerCase().includes(query) &&
                                            !tc.beschreibung.toLowerCase().includes(query)
                                          )
                                            return false;
                                        }
                                        return true;
                                      })
                                      .slice(0, 20)
                                      .map((tc, idx) => {
                                        const execution = testExecutions.find((e) => e.test_id === tc.testNr);
                                        const status = execution?.status || "pending";
                                        const isSelected = selectedTests.has(tc.testNr);

                                        const statusConfig = {
                                          passed: { icon: CheckCircle2, color: "text-emerald-600", bg: "bg-emerald-50", border: "border-emerald-200" },
                                          failed: { icon: XCircle, color: "text-red-600", bg: "bg-red-50", border: "border-red-200" },
                                          skipped: { icon: SkipForward, color: "text-amber-600", bg: "bg-amber-50", border: "border-amber-200" },
                                          pending: { icon: Clock, color: "text-slate-400", bg: "bg-slate-50", border: "border-slate-200" },
                                        }[status];

                                        const StatusIcon = statusConfig.icon;

                                        return (
                                          <motion.tr
                                            key={idx}
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: idx * 0.02 }}
                                            className={`table-row-premium group bg-white hover:bg-gradient-to-r hover:from-blue-50/30 hover:to-transparent ${isSelected ? "bg-blue-50/50" : ""}`}
                                          >
                                            <td className="px-3 py-3">
                                              <input
                                                type="checkbox"
                                                checked={isSelected}
                                                onChange={(e) => {
                                                  e.stopPropagation();
                                                  const newSelected = new Set(selectedTests);
                                                  if (e.target.checked) {
                                                    newSelected.add(tc.testNr);
                                                  } else {
                                                    newSelected.delete(tc.testNr);
                                                  }
                                                  setSelectedTests(newSelected);
                                                }}
                                                onClick={(e) => e.stopPropagation()}
                                                className="rounded border-slate-300 text-[var(--arvato-blue)] focus:ring-[var(--arvato-blue)]"
                                              />
                                            </td>
                                            <td className="px-4 py-3 font-mono text-slate-500 group-hover:text-[var(--arvato-blue)] transition-colors">
                                              {tc.testNr}
                                            </td>
                                            <td className="px-4 py-3">
                                              <select
                                                value={status}
                                                onChange={(e) => {
                                                  e.stopPropagation();
                                                  saveExecutionMutation.mutate({
                                                    test_id: tc.testNr,
                                                    status: e.target.value as any,
                                                  });
                                                }}
                                                onClick={(e) => e.stopPropagation()}
                                                className={`text-xs px-2 py-1 rounded-lg border ${statusConfig.border} ${statusConfig.bg} ${statusConfig.color} font-medium focus:outline-none focus:ring-2 focus:ring-[var(--arvato-blue)]/20`}
                                              >
                                                <option value="pending">⏳ Ausstehend</option>
                                                <option value="passed">✓ Bestanden</option>
                                                <option value="failed">✗ Fehlgeschlagen</option>
                                                <option value="skipped">⊘ Übersprungen</option>
                                              </select>
                                            </td>
                                            <td
                                              className="px-4 py-3 text-slate-700 font-medium cursor-pointer"
                                              onClick={() => {
                                                setSelectedTestCase(tc);
                                                setShowDetailModal(true);
                                                setIsEditing(false);
                                              }}
                                            >
                                              {tc.testinhalt}
                                            </td>
                                            <td
                                              className="px-4 py-3 text-slate-500 truncate max-w-xs cursor-pointer"
                                              onClick={() => {
                                                setSelectedTestCase(tc);
                                                setShowDetailModal(true);
                                                setIsEditing(false);
                                              }}
                                            >
                                              {tc.beschreibung}
                                            </td>
                                            <td className="px-4 py-3 text-right">
                                              <span
                                                onClick={() => {
                                                  setSelectedTestCase(tc);
                                                  setShowDetailModal(true);
                                                  setIsEditing(false);
                                                }}
                                                className="inline-flex items-center gap-1 px-2.5 py-1 bg-slate-100/80 text-slate-500 rounded-lg text-xs group-hover:bg-gradient-to-r group-hover:from-[var(--arvato-blue)]/10 group-hover:to-[#00D4AA]/10 group-hover:text-[var(--arvato-blue)] transition-all cursor-pointer"
                                              >
                                                Details →
                                              </span>
                                            </td>
                                          </motion.tr>
                                        );
                                      })}
                                  </tbody>
                                </table>
                                {plan.testCases.length > 20 && (
                                  <div className="px-4 py-3 bg-gradient-to-r from-slate-50 to-slate-100/50 text-xs text-slate-500 text-center border-t border-slate-200/50">
                                    + {plan.testCases.length - 20} weitere Tests
                                    (Excel exportieren für vollständige Liste)
                                  </div>
                                )}
                              </div>
                            </div>
                          )
                        )}

                        {/* Coverage Dashboard */}
                        {plan.isStructured && plan.generationState?.data?.coverage && (
                          <div className="mb-4 p-4 bg-gradient-to-br from-blue-50/50 via-teal-50/30 to-blue-50/50 rounded-xl border border-blue-100/50">
                            <h4 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                              <BarChart3 className="w-4 h-4 text-[var(--arvato-blue)]" />
                              Test Coverage Analyse
                            </h4>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                              <div>
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-xs font-medium text-slate-600">Use Cases</span>
                                  <span className="text-xs font-bold text-slate-800">
                                    {plan.generationState.data.coverage.covered_use_cases?.length || 0}
                                  </span>
                                </div>
                                <div className="w-full bg-slate-200 rounded-full h-2">
                                  <div
                                    className="bg-gradient-to-r from-blue-500 to-teal-500 h-2 rounded-full transition-all"
                                    style={{
                                      width: `${Math.min(
                                        ((plan.generationState.data.coverage.covered_use_cases?.length || 0) /
                                          Math.max(
                                            plan.generationState.data.coverage.covered_use_cases?.length || 1,
                                            1
                                          )) *
                                          100,
                                        100
                                      )}%`,
                                    }}
                                  />
                                </div>
                              </div>
                              <div>
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-xs font-medium text-slate-600">Business Rules</span>
                                  <span className="text-xs font-bold text-slate-800">
                                    {plan.generationState.data.coverage.covered_business_rules?.length || 0}
                                  </span>
                                </div>
                                <div className="w-full bg-slate-200 rounded-full h-2">
                                  <div
                                    className="bg-gradient-to-r from-emerald-500 to-teal-500 h-2 rounded-full transition-all"
                                    style={{
                                      width: `${Math.min(
                                        ((plan.generationState.data.coverage.covered_business_rules?.length || 0) /
                                          Math.max(
                                            plan.generationState.data.coverage.covered_business_rules?.length || 1,
                                            1
                                          )) *
                                          100,
                                        100
                                      )}%`,
                                    }}
                                  />
                                </div>
                              </div>
                              <div>
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-xs font-medium text-slate-600">Error Codes</span>
                                  <span className="text-xs font-bold text-slate-800">
                                    {plan.generationState.data.coverage.covered_error_codes?.length || 0}
                                  </span>
                                </div>
                                <div className="w-full bg-slate-200 rounded-full h-2">
                                  <div
                                    className="bg-gradient-to-r from-amber-500 to-orange-500 h-2 rounded-full transition-all"
                                    style={{
                                      width: `${Math.min(
                                        ((plan.generationState.data.coverage.covered_error_codes?.length || 0) /
                                          Math.max(
                                            plan.generationState.data.coverage.covered_error_codes?.length || 1,
                                            1
                                          )) *
                                          100,
                                        100
                                      )}%`,
                                    }}
                                  />
                                </div>
                              </div>
                            </div>
                            {plan.generationState.data.coverage.coverage_gaps &&
                              plan.generationState.data.coverage.coverage_gaps.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-slate-200">
                                  <p className="text-xs font-semibold text-amber-700 mb-1">Coverage Gaps:</p>
                                  <ul className="text-xs text-slate-600 space-y-1">
                                    {plan.generationState.data.coverage.coverage_gaps.map((gap: string, idx: number) => (
                                      <li key={idx} className="flex items-start gap-1">
                                        <span className="text-amber-500">•</span>
                                        <span>{gap}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                          </div>
                        )}

                        {/* Markdown Content - Collapsible */}
                        <details className="group">
                          <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-700 py-1">
                            Vollständiger Plan anzeigen
                          </summary>
                          <div className="mt-3 prose prose-sm prose-slate max-w-none prose-headings:text-slate-800 prose-h2:text-base prose-h3:text-sm">
                            <ReactMarkdown>{plan.content}</ReactMarkdown>
                          </div>
                        </details>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-slate-400 p-8">
                    <FileText className="w-10 h-10 text-slate-200 mb-3" />
                    <p className="text-sm text-slate-500">Noch kein Testplan</p>
                    <p className="text-xs text-slate-400">
                      DDD hochladen und generieren
                    </p>
                  </div>
                )
              ) : (
                /* Chat Content */
                <div className="h-full flex flex-col">
                  <DDDChat
                    projectId={id}
                    projectName={project?.name}
                    isInline={true}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Document Viewer Modal */}
      <DocumentViewer
        isOpen={viewerOpen}
        onClose={() => setViewerOpen(false)}
        docId={selectedDocId}
        apiUrl={API_URL}
      />

      {/* Delete Document Confirmation Modal */}
      {showDeleteModal && deleteDocTarget && (
        <div className="fixed inset-0 bg-slate-900/40 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden ring-1 ring-slate-900/5">
            <div className="p-6">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                  <Trash2 className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-900">
                    Dokument löschen?
                  </h3>
                  <p className="text-sm text-slate-500">
                    Diese Aktion kann nicht rückgängig gemacht werden.
                  </p>
                </div>
              </div>
              <div className="bg-slate-50 rounded-xl p-4 mb-4">
                <p className="text-sm font-medium text-slate-700 truncate">
                  {deleteDocTarget.filename}
                </p>
                <p className="text-xs text-slate-500">
                  Dokument und alle zugehörigen Chunks werden gelöscht
                </p>
              </div>
            </div>
            <div className="bg-slate-50 px-6 py-4 flex justify-end gap-3 border-t border-slate-100">
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setDeleteDocTarget(null);
                }}
                className="px-5 py-2.5 text-slate-600 hover:text-slate-900 font-medium hover:bg-white rounded-xl transition-all"
              >
                Abbrechen
              </button>
              <button
                onClick={executeDeleteDocument}
                className="px-5 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-xl font-medium shadow-lg shadow-red-500/20 transition-all"
              >
                Löschen
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Test Case Detail/Edit Modal */}
      {showDetailModal && selectedTestCase && (
        <div className="fixed inset-0 bg-slate-900/60 flex items-center justify-center z-50 p-4 backdrop-blur-sm transition-opacity duration-300">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-7xl overflow-hidden ring-1 ring-white/60 max-h-[92vh] flex flex-col transform transition-all duration-300 scale-100">
            {/* Modal Header */}
            <div className="px-8 py-6 border-b border-slate-100 flex justify-between items-start bg-gradient-to-r from-white to-slate-50/50">
              <div className="flex-1 mr-8">
                <div className="flex flex-col gap-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-1 bg-indigo-50 text-indigo-600 rounded-md text-xs font-mono font-semibold tracking-wider border border-indigo-100/50">
                        {selectedTestCase.testNr}
                      </span>
                      <span className="text-xs font-medium text-slate-400 uppercase tracking-widest">
                        Testfall Details
                      </span>
                    </div>

                    {/* Navigation Buttons - Only show if not editing or creating new */}
                    {!isEditing &&
                      testPlans.length > 0 &&
                      testPlans[0]?.testCases?.length > 0 && (
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => {
                              const currentIdx =
                                testPlans[0].testCases.findIndex(
                                  (tc) => tc.testNr === selectedTestCase.testNr,
                                );
                              if (currentIdx > 0)
                                setSelectedTestCase(
                                  testPlans[0].testCases[currentIdx - 1],
                                );
                            }}
                            disabled={
                              testPlans[0].testCases.findIndex(
                                (tc) => tc.testNr === selectedTestCase.testNr,
                              ) <= 0
                            }
                            className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg disabled:opacity-30 disabled:hover:text-slate-400 disabled:hover:bg-transparent transition-all"
                            title="Vorheriger Testfall"
                          >
                            <svg
                              className="w-5 h-5"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M15 19l-7-7 7-7"
                              />
                            </svg>
                          </button>
                          <span className="text-xs text-slate-400 font-mono w-16 text-center">
                            {testPlans[0].testCases.findIndex(
                              (tc) => tc.testNr === selectedTestCase.testNr,
                            ) + 1}{" "}
                            / {testPlans[0].testCases.length}
                          </span>
                          <button
                            onClick={() => {
                              const currentIdx =
                                testPlans[0].testCases.findIndex(
                                  (tc) => tc.testNr === selectedTestCase.testNr,
                                );
                              if (
                                currentIdx <
                                testPlans[0].testCases.length - 1
                              )
                                setSelectedTestCase(
                                  testPlans[0].testCases[currentIdx + 1],
                                );
                            }}
                            disabled={
                              testPlans[0].testCases.findIndex(
                                (tc) => tc.testNr === selectedTestCase.testNr,
                              ) >=
                              testPlans[0].testCases.length - 1
                            }
                            className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg disabled:opacity-30 disabled:hover:text-slate-400 disabled:hover:bg-transparent transition-all"
                            title="Nächster Testfall"
                          >
                            <svg
                              className="w-5 h-5"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9 5l7 7-7 7"
                              />
                            </svg>
                          </button>
                        </div>
                      )}
                  </div>

                  {isEditing ? (
                    <input
                      type="text"
                      value={selectedTestCase.testinhalt}
                      onChange={(e) =>
                        setSelectedTestCase({
                          ...selectedTestCase,
                          testinhalt: e.target.value,
                        })
                      }
                      className="w-full px-3 py-2 -ml-3 text-xl font-bold text-slate-900 border border-transparent hover:border-slate-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 rounded-lg transition-all outline-none bg-transparent focus:bg-white"
                      placeholder="Titel des Testfalls"
                    />
                  ) : (
                    <h3 className="text-xl font-bold text-slate-800 leading-tight">
                      {selectedTestCase.testinhalt}
                    </h3>
                  )}
                </div>
              </div>
              <button
                onClick={() => setShowDetailModal(false)}
                className="p-2 -mr-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-all"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content - Vertical Layout */}
            <div className="flex-1 overflow-y-auto bg-slate-50/30">
              <div className="p-8 space-y-8 max-w-5xl mx-auto">
                {/* Section: Context */}
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <div className="p-1.5 bg-blue-50 text-blue-600 rounded-lg">
                      <FileText className="w-4 h-4" />
                    </div>
                    <h4 className="text-sm font-bold text-slate-700 uppercase tracking-wide">
                      Kontext & Beschreibung
                    </h4>
                  </div>

                  <div className="flex flex-col gap-6">
                    {/* Description */}
                    <div className="group">
                      <label className="block text-xs font-semibold text-slate-500 mb-2 ml-1">
                        Beschreibung
                      </label>
                      <div
                        className={`relative rounded-xl overflow-hidden border transition-all ${isEditing ? "bg-white border-slate-300 focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-500/10 shadow-sm" : "bg-white border-slate-200"}`}
                      >
                        {isEditing ? (
                          <textarea
                            value={selectedTestCase.beschreibung}
                            onChange={(e) =>
                              setSelectedTestCase({
                                ...selectedTestCase,
                                beschreibung: e.target.value,
                              })
                            }
                            className="w-full h-24 px-4 py-3 text-sm text-slate-700 bg-transparent focus:outline-none resize-none placeholder:text-slate-400"
                            placeholder="Beschreibe den Testfall..."
                          />
                        ) : (
                          <div className="px-4 py-3 min-h-[6rem] text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">
                            {selectedTestCase.beschreibung || (
                              <span className="text-slate-400 italic">
                                Keine Beschreibung verfügbar
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Preconditions */}
                    <div className="group">
                      <label className="block text-xs font-semibold text-slate-500 mb-2 ml-1">
                        Vorbedingungen
                      </label>
                      <div
                        className={`relative rounded-xl overflow-hidden border transition-all ${isEditing ? "bg-white border-slate-300 focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-500/10 shadow-sm" : "bg-slate-50 border-slate-200"}`}
                      >
                        {isEditing ? (
                          <textarea
                            value={selectedTestCase.vorbedingung || ""}
                            onChange={(e) =>
                              setSelectedTestCase({
                                ...selectedTestCase,
                                vorbedingung: e.target.value,
                              })
                            }
                            className="w-full h-20 px-4 py-3 text-sm text-slate-700 bg-transparent focus:outline-none resize-none placeholder:text-slate-400"
                            placeholder="Was muss gegeben sein?"
                          />
                        ) : (
                          <div className="px-4 py-3 min-h-[5rem] text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">
                            {(selectedTestCase as any).vorbedingung || (
                              <span className="text-slate-400 italic">—</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="border-t border-slate-200/60"></div>

                {/* Section: Execution */}
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <div className="p-1.5 bg-emerald-50 text-emerald-600 rounded-lg">
                      <Play className="w-4 h-4" />
                    </div>
                    <h4 className="text-sm font-bold text-slate-700 uppercase tracking-wide">
                      Durchführung
                    </h4>
                  </div>

                  <div className="flex flex-col gap-6">
                    {/* Steps */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-500 mb-2 ml-1">
                        Schritte
                      </label>
                      <div
                        className={`relative rounded-xl overflow-hidden border transition-all ${isEditing ? "bg-white border-slate-300 focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-500/10 shadow-sm" : "bg-white border-slate-200"}`}
                      >
                        {isEditing ? (
                          <textarea
                            value={(selectedTestCase as any).schritte || ""}
                            onChange={(e) =>
                              setSelectedTestCase({
                                ...selectedTestCase,
                                schritte: e.target.value,
                              } as any)
                            }
                            className="w-full h-48 px-4 py-3 text-sm text-slate-700 bg-transparent focus:outline-none resize-none placeholder:text-slate-400 font-mono"
                            placeholder="1. Schritt..."
                          />
                        ) : (
                          <div className="px-4 py-3 min-h-[10rem] text-sm text-slate-600 leading-relaxed whitespace-pre-wrap font-mono bg-slate-50/50">
                            <div className="prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-li:my-0">
                              <ReactMarkdown>
                                {(selectedTestCase as any).schritte || ""}
                              </ReactMarkdown>
                            </div>
                            {!(selectedTestCase as any).schritte && (
                              <span className="text-slate-400 italic">—</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Expected Result */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-500 mb-2 ml-1">
                        Erwartetes Ergebnis
                      </label>
                      <div
                        className={`relative rounded-xl overflow-hidden border transition-all ${isEditing ? "bg-white border-slate-300 focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-500/10 shadow-sm" : "bg-green-50/50 border-green-100"}`}
                      >
                        {isEditing ? (
                          <textarea
                            value={
                              (selectedTestCase as any).erwartetes_ergebnis ||
                              ""
                            }
                            onChange={(e) =>
                              setSelectedTestCase({
                                ...selectedTestCase,
                                erwartetes_ergebnis: e.target.value,
                              } as any)
                            }
                            className="w-full h-32 px-4 py-3 text-sm text-slate-700 bg-transparent focus:outline-none resize-none placeholder:text-slate-400"
                            placeholder="Was soll passieren?"
                          />
                        ) : (
                          <div className="px-4 py-3 min-h-[6rem] text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
                            {(selectedTestCase as any).erwartetes_ergebnis || (
                              <span className="text-slate-400 italic">—</span>
                            )}
                          </div>
                        )}
                        {!isEditing &&
                          (selectedTestCase as any).erwartetes_ergebnis && (
                            <div className="absolute top-2 right-2">
                              <CheckCircle className="w-4 h-4 text-green-500/50" />
                            </div>
                          )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="px-8 py-5 bg-white border-t border-slate-100 flex justify-end gap-3 z-10">
              <button
                onClick={() => setShowDetailModal(false)}
                className="px-5 py-2.5 text-slate-500 hover:text-slate-700 font-medium hover:bg-slate-50 rounded-xl transition-all"
              >
                Schließen
              </button>
              {isEditing ? (
                <button
                  onClick={saveTestCaseChanges}
                  className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 active:scale-95 text-white rounded-xl font-medium shadow-lg shadow-indigo-500/20 transition-all flex items-center gap-2"
                >
                  <Check className="w-4 h-4" />
                  Speichern
                </button>
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-6 py-2.5 bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 hover:border-slate-300 active:scale-95 rounded-xl font-medium transition-all flex items-center gap-2 shadow-sm"
                >
                  <PenTool className="w-4 h-4 text-slate-400" />
                  Bearbeiten
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      <DocumentSelector
        isOpen={showDocSelector}
        onClose={() => setShowDocSelector(false)}
        selectedDocIds={selectedDocIds}
        onSelectionChange={setSelectedDocIds}
        apiUrl={API_URL}
      />
    </AppLayout>
  );
}
