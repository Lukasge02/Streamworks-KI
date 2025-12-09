"""
XML Router - API Endpoints für XML Generation und Preview
"""
from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, Dict, Any, List


# from domains.chat.session import session_manager
from services.db import db
from .service import xml_service


router = APIRouter(prefix="/api/xml", tags=["XML"])


class GenerateRequest(BaseModel):
    session_id: str


class ValidateRequest(BaseModel):
    xml_content: str
    job_type: Optional[str] = "FILE_TRANSFER"


class RegenerateRequest(BaseModel):
    session_id: str
    updated_params: Dict[str, Any]


class StreamSummary(BaseModel):
    id: str
    filename: str
    created_at: str
    job_type: Optional[str] = None





@router.post("/regenerate")
async def regenerate_xml(req: RegenerateRequest):
    """Regenerate XML with updated parameters from the editor"""
    session = db.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    job_type = session.get("job_type") or "STANDARD"
    
    # Merge existing params with updates (updates take priority)
    existing_params = session.get("params", {})
    merged_params = {**existing_params, **req.updated_params}
    
    # Filter out empty string values (treat as unset)
    merged_params = {k: v for k, v in merged_params.items() if v != ""}
    
    # Update session with new params
    # Update session with new params
    session["params"] = merged_params
    db.save_session(req.session_id, session)
    
    # Generate new XML and validate
    xml_content, validation = xml_service.generate_and_validate(job_type, merged_params)
    
    # Save to Supabase Stream History if valid
    # Save to Supabase Stream History if valid
    if validation["is_valid"]:
        try:
            db.save_stream(
                filename=merged_params.get("stream_name", "Unnamed"),
                content=xml_content,
                metadata=merged_params,
                job_type=job_type
            )
        except Exception as e:
            print(f"Supabase stream save error: {e}")

    return {
        "xml": xml_content,
        "validation": validation,
        "params": merged_params
    }


@router.post("/generate")
async def generate_xml(req: GenerateRequest):
    """Generate XML from session parameters"""
    session = db.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    job_type = session.get("job_type") or "STANDARD"
    params = session.get("params", {})
    
    xml_content, validation = xml_service.generate_and_validate(job_type, params)
    
    return {
        "xml": xml_content,
        "job_type": job_type,
        "params": params,
        "validation": validation
    }


@router.post("/preview")
async def preview_xml(session_id: str = Form(...)):
    """
    Generate XML preview with Monaco Editor and editable parameters.
    """
    import json
    
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    job_type = session.get("job_type") or "STANDARD"
    params = session.get("params", {})
    
    xml_content, validation = xml_service.generate_and_validate(job_type, params)
    
    # All parameters with metadata for rendering
    all_params = [
        {"key": "stream_name", "label": "Stream-Name", "type": "text", "required": True},
        {"key": "source_agent", "label": "Quell-Server", "type": "text", "required": job_type == "FILE_TRANSFER"},
        {"key": "target_agent", "label": "Ziel-Server", "type": "text", "required": job_type == "FILE_TRANSFER"},
        {"key": "source_file_pattern", "label": "Quell-Dateipfad", "type": "text", "required": job_type == "FILE_TRANSFER"},
        {"key": "target_file_path", "label": "Ziel-Verzeichnis", "type": "text", "required": False},
        {"key": "agent_detail", "label": "Agent", "type": "text", "required": job_type == "STANDARD"},
        {"key": "main_script", "label": "Haupt-Script", "type": "text", "required": job_type == "STANDARD"},
        {"key": "schedule", "label": "Zeitplan", "type": "dropdown", "options": ["", "täglich", "wöchentlich", "monatlich", "stündlich", "werktags"], "required": False},
        {"key": "start_time", "label": "Startzeit", "type": "time", "required": False},
        {"key": "source_file_delete_flag", "label": "Quelle löschen", "type": "dropdown", "options": ["", "true", "false"], "required": False},
        {"key": "target_file_exists_handling", "label": "Ziel existiert", "type": "dropdown", "options": ["", "Overwrite", "Skip", "Abort"], "required": False},
        {"key": "contact_first_name", "label": "Kontakt Vorname", "type": "text", "required": False},
        {"key": "contact_last_name", "label": "Kontakt Nachname", "type": "text", "required": False},
        {"key": "company_name", "label": "Firma", "type": "text", "required": False},
    ]
    
    # Build editable parameter HTML
    params_html = ""
    for p in all_params:
        value = params.get(p["key"], "")
        is_empty = not value
        empty_class = "empty" if is_empty else ""
        required_class = "required" if p.get("required") else ""
        
        if p["type"] == "dropdown":
            options_html = "".join(
                f'<option value="{opt}" {"selected" if opt == value else ""}>{opt if opt else "—"}</option>'
                for opt in p.get("options", [])
            )
            input_html = f'<select class="param-input" data-key="{p["key"]}" onchange="updateParam(this)">{options_html}</select>'
        elif p["type"] == "time":
            input_html = f'<input type="time" class="param-input" data-key="{p["key"]}" value="{value}" onchange="updateParam(this)">'
        else:
            input_html = f'<input type="text" class="param-input" data-key="{p["key"]}" value="{value}" placeholder="—" onchange="updateParam(this)">'
        
        params_html += f'''
        <div class="param-row {empty_class} {required_class}">
            <label class="param-label">{p["label"]}</label>
            {input_html}
        </div>'''
    
    job_type_display = {"FILE_TRANSFER": "Dateitransfer", "STANDARD": "Standard Job", "SAP": "SAP Job"}.get(job_type, job_type)
    
    # Validation status
    status_class = "valid" if validation["is_valid"] else "invalid"
    status_icon = "✓" if validation["is_valid"] else "✗"
    status_text = "XML Validierung erfolgreich" if validation["is_valid"] else f"{len(validation['issues'])} Fehler"
    
    issues_html = ""
    if validation["issues"]:
        issues_html = '<div class="issues">' + "".join(
            f'<div class="issue">Zeile {issue["line"]}: {issue["message"]}</div>' 
            for issue in validation["issues"]
        ) + '</div>'
    
    # JSON params for JavaScript
    params_json = json.dumps(params)
    
    html_content = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XML Editor - {validation["stream_name"]}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: #f1f5f9;
            color: #1e293b;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #004899 0%, #0066cc 100%);
            color: white;
            padding: 0 1.5rem;
            height: 56px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
        }}
        
        .header-left {{ display: flex; align-items: center; gap: 0.75rem; }}
        .header h1 {{ font-size: 1rem; font-weight: 600; }}
        .badge {{ background: rgba(255,255,255,0.2); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; }}
        
        .main {{
            flex: 1;
            display: flex;
            overflow: hidden;
        }}
        
        /* Sidebar */
        .sidebar {{
            width: 340px;
            background: white;
            border-right: 1px solid #e2e8f0;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            flex-shrink: 0;
        }}
        
        .sidebar-section {{
            padding: 1rem 1.25rem;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .sidebar-title {{
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748b;
            margin-bottom: 0.75rem;
        }}
        
        .status-card {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem;
            border-radius: 6px;
        }}
        
        .status-card.valid {{ background: #ecfdf5; border: 1px solid #a7f3d0; }}
        .status-card.invalid {{ background: #fef2f2; border: 1px solid #fecaca; }}
        
        .status-icon {{
            width: 24px; height: 24px;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 0.75rem;
        }}
        .status-card.valid .status-icon {{ background: #10b981; color: white; }}
        .status-card.invalid .status-icon {{ background: #ef4444; color: white; }}
        .status-text {{ font-weight: 500; font-size: 0.8125rem; }}
        .status-card.valid .status-text {{ color: #047857; }}
        .status-card.invalid .status-text {{ color: #b91c1c; }}
        
        .issues {{ margin-top: 0.5rem; }}
        .issue {{ font-size: 0.75rem; color: #b91c1c; padding: 0.375rem; background: #fef2f2; border-radius: 4px; margin-bottom: 0.25rem; }}
        
        /* Parameter Rows */
        .param-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #f1f5f9;
            gap: 0.75rem;
        }}
        .param-row:last-child {{ border-bottom: none; }}
        .param-row.empty .param-label {{ color: #94a3b8; }}
        .param-row.required .param-label::after {{ content: " *"; color: #ef4444; }}
        
        .param-label {{
            font-size: 0.75rem;
            color: #475569;
            flex-shrink: 0;
            width: 120px;
        }}
        
        .param-input {{
            flex: 1;
            font-size: 0.75rem;
            padding: 0.375rem 0.5rem;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            background: white;
            color: #1e293b;
            max-width: 180px;
        }}
        .param-input:focus {{
            outline: none;
            border-color: #004899;
            box-shadow: 0 0 0 2px rgba(0, 72, 153, 0.1);
        }}
        .param-row.empty .param-input {{
            color: #94a3b8;
            border-style: dashed;
        }}
        
        select.param-input {{
            cursor: pointer;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.5rem;
        }}
        .stat-box {{
            background: #f8fafc;
            padding: 0.5rem;
            border-radius: 4px;
            text-align: center;
        }}
        .stat-value {{ font-size: 1rem; font-weight: 700; color: #004899; }}
        .stat-label {{ font-size: 0.6rem; color: #64748b; }}
        
        /* Editor Area */
        .editor-area {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        
        .toolbar {{
            padding: 0.75rem 1rem;
            background: white;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }}
        
        .toolbar-title {{ font-weight: 600; font-size: 0.875rem; color: #1e293b; }}
        .toolbar-actions {{ display: flex; gap: 0.5rem; }}
        
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.375rem;
            padding: 0.5rem 0.875rem;
            border-radius: 5px;
            font-size: 0.8125rem;
            font-weight: 500;
            border: none;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .btn-outline {{ background: white; color: #475569; border: 1px solid #e2e8f0; }}
        .btn-outline:hover {{ background: #f8fafc; }}
        .btn-success {{ background: #10b981; color: white; }}
        .btn-success:hover {{ background: #059669; }}
        .btn-primary {{ background: #004899; color: white; }}
        .btn-primary:hover {{ background: #003b7a; }}
        
        #editor-container {{
            flex: 1;
            overflow: hidden;
        }}
        
        .footer {{
            background: white;
            border-top: 1px solid #e2e8f0;
            padding: 0.625rem 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }}
        .footer-info {{ font-size: 0.75rem; color: #64748b; }}
        
        .toast {{
            position: fixed;
            bottom: 1.5rem;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: #1e293b;
            color: white;
            padding: 0.625rem 1.25rem;
            border-radius: 6px;
            font-weight: 500;
            font-size: 0.875rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            opacity: 0;
            transition: all 0.25s ease;
            z-index: 100;
        }}
        .toast.show {{ transform: translateX(-50%) translateY(0); opacity: 1; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-left">
            <h1>📄 Streamworks XML Editor</h1>
        </div>
        <div class="header-right">
            <span class="badge">{job_type_display}</span>
            <span class="badge">{validation["stream_name"]}</span>
        </div>
    </header>
    
    <main class="main">
        <aside class="sidebar">
            <div class="sidebar-section">
                <div class="sidebar-title">Validierung</div>
                <div class="status-card {status_class}">
                    <div class="status-icon">{status_icon}</div>
                    <div class="status-text">{status_text}</div>
                </div>
                {issues_html}
            </div>
            
            <div class="sidebar-section" style="flex: 1; overflow-y: auto;">
                <div class="sidebar-title">Parameter bearbeiten</div>
                {params_html}
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-title">Statistiken</div>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-value" id="stat-elements">{validation["element_count"]}</div>
                        <div class="stat-label">Elemente</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value" id="stat-bytes">{validation["xml_length"]:,}</div>
                        <div class="stat-label">Bytes</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value" id="stat-lines">—</div>
                        <div class="stat-label">Zeilen</div>
                    </div>
                </div>
                <button class="btn btn-primary" style="width: 100%; margin-top: 0.75rem;" onclick="regenerateXML()">
                    🔄 XML neu generieren
                </button>
            </div>
        </aside>
        
        <div class="editor-area">
            <div class="toolbar">
                <span class="toolbar-title">XML Vorschau</span>
                <div class="toolbar-actions">
                    <button class="btn btn-outline" onclick="formatXML()">🎨 Formatieren</button>
                    <button class="btn btn-outline" onclick="copyXML()">📋 Kopieren</button>
                    <button class="btn btn-success" onclick="downloadXML()">⬇ Herunterladen</button>
                </div>
            </div>
            <div id="editor-container">
                <div id="editor-loading" style="display: flex; align-items: center; justify-content: center; height: 100%; background: #1e1e1e; color: #888;">
                    <span>Monaco Editor wird geladen...</span>
                </div>
                <textarea id="editor-fallback" style="display: none; width: 100%; height: 100%; font-family: 'Consolas', 'Monaco', monospace; font-size: 13px; background: #1e1e1e; color: #d4d4d4; border: none; padding: 1rem; resize: none;"></textarea>
            </div>
        </div>
    </main>
    
    <footer class="footer">
        <span class="footer-info">Session: {session_id[:8]}... | Generiert am {__import__('datetime').datetime.now().strftime('%d.%m.%Y um %H:%M')}</span>
        <button class="btn btn-outline" onclick="window.close()">Schließen</button>
    </footer>
    
    <div class="toast" id="toast"></div>
    
    <!-- Monaco Editor -->
    <script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs/loader.js"></script>
    <script>
        let editor;
        let currentParams = {params_json};
        const sessionId = "{session_id}";
        const jobType = "{job_type}";
        // Initialize Monaco Editor with timeout fallback
        const xmlContent = {json.dumps(xml_content)};
        let monacoLoaded = false;
        
        // Timeout: Falls Monaco nicht in 5 Sekunden lädt, Fallback zeigen
        const fallbackTimeout = setTimeout(function() {{
            if (!monacoLoaded) {{
                console.warn('Monaco Editor konnte nicht geladen werden, zeige Fallback');
                document.getElementById('editor-loading').style.display = 'none';
                const fallback = document.getElementById('editor-fallback');
                fallback.style.display = 'block';
                fallback.value = xmlContent;
            }}
        }}, 5000);
        
        require.config({{ paths: {{ vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs' }} }});
        require(['vs/editor/editor.main'], function() {{
            monacoLoaded = true;
            clearTimeout(fallbackTimeout);
            
            // Verstecke Loading und Fallback
            document.getElementById('editor-loading').style.display = 'none';
            document.getElementById('editor-fallback').style.display = 'none';
            
            editor = monaco.editor.create(document.getElementById('editor-container'), {{
                value: xmlContent,
                language: 'xml',
                theme: 'vs-dark',
                automaticLayout: true,
                minimap: {{ enabled: true }},
                fontSize: 13,
                lineNumbers: 'on',
                wordWrap: 'on',
                scrollBeyondLastLine: false,
                readOnly: false,
                formatOnPaste: true,
                formatOnType: true
            }});
            
            // Update stats
            updateStats();
            editor.onDidChangeModelContent(updateStats);
        }});
        
        function updateStats() {{
            if (!editor) return;
            const content = editor.getValue();
            document.getElementById('stat-lines').textContent = content.split('\\n').length;
            document.getElementById('stat-bytes').textContent = new Blob([content]).size.toLocaleString();
        }}
        
        function showToast(message) {{
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2000);
        }}
        
        function updateParam(el) {{
            currentParams[el.dataset.key] = el.value;
            
            // Update row styling
            const row = el.closest('.param-row');
            if (el.value) {{
                row.classList.remove('empty');
            }} else {{
                row.classList.add('empty');
            }}
        }}
        
        async function regenerateXML() {{
            showToast('XML wird neu generiert...');
            
            try {{
                const response = await fetch('/api/xml/regenerate', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        session_id: sessionId,
                        updated_params: currentParams
                    }})
                }});
                
                if (!response.ok) {{
                    throw new Error('Fehler beim Regenerieren');
                }}
                
                const data = await response.json();
                
                // Update Monaco Editor content
                if (editor && data.xml) {{
                    editor.setValue(data.xml);
                }}
                
                // Update current params
                currentParams = data.params || currentParams;
                
                // Update validation status in sidebar
                const statusCard = document.querySelector('.status-card');
                const statusIcon = document.querySelector('.status-icon');
                const statusText = document.querySelector('.status-text');
                const issuesContainer = document.querySelector('.issues');
                
                if (data.validation) {{
                    if (data.validation.is_valid) {{
                        statusCard.className = 'status-card valid';
                        statusIcon.textContent = '✓';
                        statusText.textContent = 'XML Validierung erfolgreich';
                        if (issuesContainer) issuesContainer.innerHTML = '';
                    }} else {{
                        statusCard.className = 'status-card invalid';
                        statusIcon.textContent = '✗';
                        statusText.textContent = (data.validation.issues?.length || 0) + ' Fehler';
                        if (issuesContainer) {{
                            issuesContainer.innerHTML = data.validation.issues
                                .map(issue => `<div class="issue">Zeile ${issue.line}: ${issue.message}</div>`)
                                .join('');
                        }}
                    }}
                    
                    // Update stats
                    document.getElementById('stat-elements').textContent = data.validation.element_count || '—';
                }}
                
                showToast('✅ XML erfolgreich neu generiert');
            }} catch (error) {{
                console.error('Regenerate error:', error);
                showToast('❌ Fehler beim Regenerieren: ' + error.message);
            }}
        }}
        
        function formatXML() {{
            if (!editor) return;
            editor.getAction('editor.action.formatDocument').run();
            showToast('XML formatiert');
        }}
        
        function copyXML() {{
            if (!editor) return;
            navigator.clipboard.writeText(editor.getValue()).then(() => {{
                showToast('📋 In Zwischenablage kopiert');
            }});
        }}
        
        function downloadXML() {{
            if (!editor) return;
            const content = editor.getValue();
            const streamName = currentParams.stream_name || 'stream';
            const blob = new Blob([content], {{ type: 'application/xml' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = (streamName.startsWith('GECK003_') ? streamName : 'GECK003_' + streamName) + '.xml';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            showToast('⬇ Download gestartet');
        }}
    </script>
</body>
</html>'''
    
    return Response(content=html_content, media_type="text/html")


@router.post("/validate")
async def validate_xml(req: ValidateRequest):
    """Validate XML content"""
    validation = xml_service.validate(req.xml_content, req.job_type)
    return validation


@router.get("/download/{session_id}")
async def download_xml(session_id: str):
    """Download XML as file"""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    job_type = session.get("job_type") or "STANDARD"
    params = session.get("params", {})
    
    xml_content = xml_service.generate(job_type, params)
    stream_name = params.get("stream_name", "stream")
    
    # Add GECK003_ prefix if not present
    if not stream_name.startswith("GECK003_"):
        stream_name = f"GECK003_{stream_name}"
    
    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={
            "Content-Disposition": f'attachment; filename="{stream_name}.xml"'
        }
    )


@router.get("/", response_model=List[StreamSummary])
async def list_streams():
    """List recently generated streams"""
    streams = db.get_user_streams(limit=50)
    result = []
    for s in streams:
        meta = s.get("metadata") or {}
        # Parse timestamp safely if needed, but string passthrough is fine for now
        result.append({
            "id": s["id"],
            "filename": s["filename"],
            "created_at": s["created_at"],
            "job_type": meta.get("job_type", "UNKNOWN")
        })
    return result


@router.get("/{stream_id}")
async def get_stream_details(stream_id: str):
    """Get full stream details"""
    stream = db.get_stream(stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")
    return stream
