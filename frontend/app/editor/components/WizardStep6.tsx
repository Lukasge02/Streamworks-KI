"use client";

import { useState } from "react";

interface WizardSession {
    session_id: string;
    params: Record<string, string | boolean | number>;
    detected_job_type: string | null;
}

interface XmlResult {
    xml: string;
    job_type: string;
    params: Record<string, unknown>;
}

interface Props {
    session: WizardSession | null;
    onSave: (stepId: string, data: Record<string, unknown>, shouldAdvance?: boolean) => Promise<void>;
    onGenerate: () => Promise<XmlResult | null>;
    isLoading: boolean;
}

export default function WizardStep6Preview({ session, onSave, onGenerate, isLoading }: Props) {
    const [xmlResult, setXmlResult] = useState<XmlResult | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);

    const handleGenerate = async () => {
        setIsGenerating(true);
        const result = await onGenerate();
        if (result) {
            setXmlResult(result);
        }
        setIsGenerating(false);
    };

    const handleDownload = () => {
        if (!xmlResult) return;

        const blob = new Blob([xmlResult.xml], { type: "application/xml" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${session?.params.stream_name || "stream"}.xml`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const handleCopyToClipboard = () => {
        if (!xmlResult) return;
        navigator.clipboard.writeText(xmlResult.xml);
    };

    const jobType = session?.detected_job_type || (session?.params.job_type as string) || "STANDARD";

    return (
        <div>
            <h2 style={{
                fontSize: "1.25rem",
                fontWeight: 600,
                color: "#1a1a1a",
                marginBottom: "0.5rem",
            }}>
                ✅ Schritt 6: Vorschau & Details
            </h2>
            <p style={{ color: "#6b7280", marginBottom: "1rem" }}>
                Überprüfen Sie Ihre Eingaben und wechseln Sie zur Detail-Ansicht für die finale Generierung.
            </p>

            {/* Summary */}
            <div style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "1rem",
                marginBottom: "1rem",
            }}>
                {/* Stream Info */}
                <div style={{
                    background: "white",
                    border: "1px solid #e5e7eb",
                    borderRadius: "12px",
                    padding: "1.25rem",
                }}>
                    <h3 style={{
                        fontSize: "0.875rem",
                        fontWeight: 600,
                        color: "#6b7280",
                        marginBottom: "1rem",
                        textTransform: "uppercase",
                    }}>
                        📝 Stream-Info
                    </h3>
                    <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                        <div style={{ display: "flex", justifyContent: "space-between" }}>
                            <span style={{ color: "#6b7280" }}>Name:</span>
                            <span style={{ fontWeight: 500 }}>{session?.params.stream_name || "—"}</span>
                        </div>
                        <div style={{ display: "flex", justifyContent: "space-between" }}>
                            <span style={{ color: "#6b7280" }}>Typ:</span>
                            <span style={{
                                background: "#0082D9",
                                color: "white",
                                padding: "0.125rem 0.5rem",
                                borderRadius: "4px",
                                fontSize: "0.75rem",
                            }}>
                                {jobType}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Contact Info */}
                <div style={{
                    background: "white",
                    border: "1px solid #e5e7eb",
                    borderRadius: "12px",
                    padding: "1.25rem",
                }}>
                    <h3 style={{
                        fontSize: "0.875rem",
                        fontWeight: 600,
                        color: "#6b7280",
                        marginBottom: "1rem",
                        textTransform: "uppercase",
                    }}>
                        👤 Kontakt
                    </h3>
                    <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                        <div style={{ display: "flex", justifyContent: "space-between" }}>
                            <span style={{ color: "#6b7280" }}>Name:</span>
                            <span style={{ fontWeight: 500 }}>
                                {session?.params.contact_first_name} {session?.params.contact_last_name}
                            </span>
                        </div>
                        {session?.params.company_name && (
                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                                <span style={{ color: "#6b7280" }}>Firma:</span>
                                <span>{session?.params.company_name}</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Schedule Info */}
                <div style={{
                    background: "white",
                    border: "1px solid #e5e7eb",
                    borderRadius: "12px",
                    padding: "1.25rem",
                }}>
                    <h3 style={{
                        fontSize: "0.875rem",
                        fontWeight: 600,
                        color: "#6b7280",
                        marginBottom: "1rem",
                        textTransform: "uppercase",
                    }}>
                        📅 Zeitplan
                    </h3>
                    <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                        <div style={{ display: "flex", justifyContent: "space-between" }}>
                            <span style={{ color: "#6b7280" }}>Frequenz:</span>
                            <span style={{ fontWeight: 500 }}>{session?.params.schedule || "täglich"}</span>
                        </div>
                        {session?.params.start_time && (
                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                                <span style={{ color: "#6b7280" }}>Startzeit:</span>
                                <span>{session?.params.start_time}</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Job Details */}
                <div style={{
                    background: "white",
                    border: "1px solid #e5e7eb",
                    borderRadius: "12px",
                    padding: "1.25rem",
                }}>
                    <h3 style={{
                        fontSize: "0.875rem",
                        fontWeight: 600,
                        color: "#6b7280",
                        marginBottom: "1rem",
                        textTransform: "uppercase",
                    }}>
                        🔧 Job-Details
                    </h3>
                    <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", fontSize: "0.875rem" }}>
                        {jobType === "STANDARD" && (
                            <>
                                <div><span style={{ color: "#6b7280" }}>Agent:</span> {session?.params.agent_detail}</div>
                                <div><span style={{ color: "#6b7280" }}>Script:</span> {(session?.params.main_script as string)?.substring(0, 30)}...</div>
                            </>
                        )}
                        {jobType === "FILE_TRANSFER" && (
                            <>
                                <div><span style={{ color: "#6b7280" }}>Von:</span> {session?.params.source_agent}</div>
                                <div><span style={{ color: "#6b7280" }}>Nach:</span> {session?.params.target_agent}</div>
                            </>
                        )}
                        {jobType === "SAP" && (
                            <>
                                <div><span style={{ color: "#6b7280" }}>System:</span> {session?.params.sap_system}</div>
                                <div><span style={{ color: "#6b7280" }}>Report:</span> {session?.params.sap_report}</div>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {/* Finish Button */}
            <div style={{ textAlign: "center", marginTop: "2rem" }}>
                <button
                    onClick={() => onSave("preview", {}, true)}
                    disabled={isLoading}
                    style={{
                        padding: "1rem 3rem",
                        background: "linear-gradient(135deg, #0082D9 0%, #006BB3 100%)",
                        color: "white",
                        border: "none",
                        borderRadius: "12px",
                        fontWeight: 600,
                        fontSize: "1.125rem",
                        cursor: isLoading ? "not-allowed" : "pointer",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "0.75rem",
                        boxShadow: "0 4px 12px rgba(0, 130, 217, 0.3)",
                    }}
                >
                    {isLoading ? "Lade..." : "🔍 Zur Detail-Ansicht & Generierung"}
                </button>
            </div>

        </div>
    );
}
