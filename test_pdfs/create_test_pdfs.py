#!/usr/bin/env python3
"""
PDF Test Document Generator
Erstellt verschiedene PDF-Testdokumente für Chunking-Evaluierung
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import os

def create_mini_pdf():
    """Erstellt sehr kurzes PDF (wie Kündigung-Mietvertrag.pdf)"""
    filename = "01_mini_kuendigung.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Titel
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1  # center
    )
    
    story.append(Paragraph("Kündigung des Mietvertrags", title_style))
    story.append(Spacer(1, 20))
    
    # Inhalt
    content = [
        "Sehr geehrte Damen und Herren,",
        "",
        "hiermit kündige ich den mit Ihnen abgeschlossenen Mietvertrag für die Wohnung in der Musterstraße 123, 12345 Berlin, ordentlich und fristgerecht zum 31.12.2024.",
        "",
        "Die Wohnung wurde am 01.01.2022 von mir übernommen.",
        "",
        "Mit freundlichen Grüßen",
        "Max Mustermann",
        "",
        "Datum: 30.09.2024"
    ]
    
    for line in content:
        if line:
            story.append(Paragraph(line, styles['Normal']))
        story.append(Spacer(1, 8))
    
    doc.build(story)
    return filename

def create_small_pdf():
    """Erstellt kleines PDF mit mehreren Absätzen"""
    filename = "02_small_bewerbung.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Titel
    story.append(Paragraph("Bewerbung als Software-Entwickler", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    # Anschreiben
    content_sections = [
        ("Sehr geehrte Damen und Herren,", "Normal"),
        ("", "Normal"),
        ("mit großem Interesse habe ich Ihre Stellenausschreibung für die Position als Software-Entwickler gelesen. Als erfahrener Entwickler mit 5 Jahren Berufserfahrung in Python und JavaScript möchte ich mich hiermit für diese spannende Position bewerben.", "Normal"),
        ("", "Normal"),
        ("Meine Qualifikationen:", "Heading2"),
        ("• Bachelor-Abschluss in Informatik", "Normal"),
        ("• 5 Jahre Erfahrung in Full-Stack Entwicklung", "Normal"),
        ("• Expertise in Python, JavaScript, React und Node.js", "Normal"),
        ("• Erfahrung mit Cloud-Technologien (AWS, Docker)", "Normal"),
        ("• Agile Entwicklungsmethoden (Scrum, Kanban)", "Normal"),
        ("", "Normal"),
        ("In meiner aktuellen Position bei der TechCorp GmbH entwickle ich hauptsächlich Web-Anwendungen und APIs. Dabei arbeite ich eng mit dem Product Owner und dem Design-Team zusammen, um benutzerfreundliche und effiziente Lösungen zu entwickeln.", "Normal"),
        ("", "Normal"),
        ("Über eine Einladung zu einem persönlichen Gespräch würde ich mich sehr freuen.", "Normal"),
        ("", "Normal"),
        ("Mit freundlichen Grüßen", "Normal"),
        ("Sarah Schmidt", "Normal")
    ]
    
    for text, style in content_sections:
        if text:
            story.append(Paragraph(text, styles[style]))
        story.append(Spacer(1, 8))
    
    doc.build(story)
    return filename

def create_medium_pdf():
    """Erstellt mittleres PDF mit strukturiertem Inhalt"""
    filename = "03_medium_projektplan.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Titel
    story.append(Paragraph("Projektplan: E-Learning Platform", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    sections = [
        ("1. Projektziele", "Heading2", [
            "Die E-Learning Platform soll eine moderne, benutzerfreundliche Umgebung für Online-Kurse bieten. Ziel ist es, bis zu 10.000 gleichzeitige Nutzer zu unterstützen und eine hohe Verfügbarkeit von 99.9% zu gewährleisten.",
            "Hauptziele: Skalierbare Architektur, intuitive Benutzeroberfläche, umfassende Analytics, mobile Unterstützung."
        ]),
        
        ("2. Technische Anforderungen", "Heading2", [
            "Frontend: React 18 mit TypeScript für eine moderne, responsive Benutzeroberfläche. Die Anwendung muss auf Desktop, Tablet und Smartphone optimiert sein.",
            "Backend: Node.js mit Express Framework, PostgreSQL als Hauptdatenbank, Redis für Caching und Session-Management.",
            "Infrastructure: AWS Cloud mit Auto-Scaling, Load Balancer, CDN für statische Inhalte. Docker Container für einfache Deployment-Prozesse."
        ]),
        
        ("3. Entwicklungsplan", "Heading2", [
            "Phase 1 (Wochen 1-4): Grundgerüst und Benutzer-Management. Authentifizierung, Autorisierung, grundlegende UI-Komponenten.",
            "Phase 2 (Wochen 5-8): Kurs-Management System. Erstellung, Bearbeitung und Verwaltung von Online-Kursen durch Dozenten.",
            "Phase 3 (Wochen 9-12): Lern-Features. Video-Player, Quizzes, Fortschritts-Tracking, Zertifikate."
        ]),
        
        ("4. Qualitätssicherung", "Heading2", [
            "Umfassende Test-Strategie: Unit-Tests (Jest), Integration-Tests (Supertest), End-to-End Tests (Playwright).",
            "Code-Review Prozess: Alle Änderungen müssen von mindestens zwei Entwicklern reviewed werden.",
            "Performance-Monitoring: Kontinuierliche Überwachung der Anwendungsperformance und Benutzer-Experience."
        ]),
        
        ("5. Zeitplan und Meilensteine", "Heading2", [
            "Gesamtprojektdauer: 12 Wochen mit wöchentlichen Sprint-Reviews.",
            "Wichtige Meilensteine: MVP nach 6 Wochen, Beta-Version nach 10 Wochen, Go-Live nach 12 Wochen.",
            "Risiko-Management: Pufferzeiten für unvorhergesehene Herausforderungen eingeplant."
        ])
    ]
    
    for section_title, heading_style, paragraphs in sections:
        story.append(Paragraph(section_title, styles[heading_style]))
        story.append(Spacer(1, 12))
        
        for paragraph in paragraphs:
            story.append(Paragraph(paragraph, styles['Normal']))
            story.append(Spacer(1, 8))
        
        story.append(Spacer(1, 16))
    
    doc.build(story)
    return filename

def create_table_pdf():
    """Erstellt PDF mit Tabellen (wie parkpreiseuebersicht-fra.pdf)"""
    filename = "04_table_verkaufsbericht.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Titel
    story.append(Paragraph("Quartalsbericht Q3 2024 - Verkaufszahlen", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    # Erste Tabelle: Regional Performance
    story.append(Paragraph("Regionale Verkaufsentwicklung", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    regional_data = [
        ['Region', 'Q1 2024', 'Q2 2024', 'Q3 2024', 'Wachstum %'],
        ['Deutschland', '125.000', '138.000', '152.000', '+21.6%'],
        ['Österreich', '45.000', '52.000', '58.000', '+28.9%'],
        ['Schweiz', '38.000', '42.000', '47.000', '+23.7%'],
        ['Niederlande', '62.000', '68.000', '75.000', '+21.0%'],
        ['Gesamt', '270.000', '300.000', '332.000', '+23.0%']
    ]
    
    regional_table = Table(regional_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    regional_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(regional_table)
    story.append(Spacer(1, 20))
    
    # Zweite Tabelle: Top Produkte
    story.append(Paragraph("Top 10 Produkte nach Umsatz", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    product_data = [
        ['Rang', 'Produktname', 'Umsatz €', 'Stückzahl', 'Ø Preis €'],
        ['1', 'Premium Laptop Pro', '450.000', '1.500', '300.00'],
        ['2', 'Smartphone Ultra X', '380.000', '1.900', '200.00'],
        ['3', 'Gaming Monitor 4K', '320.000', '800', '400.00'],
        ['4', 'Wireless Kopfhörer', '280.000', '2.800', '100.00'],
        ['5', 'Tablet Pro 11"', '250.000', '1.000', '250.00'],
        ['6', 'Bluetooth Lautsprecher', '220.000', '4.400', '50.00'],
        ['7', 'Smartwatch Series 5', '200.000', '1.333', '150.00'],
        ['8', 'USB-C Docking Station', '180.000', '1.200', '150.00'],
        ['9', 'Externe SSD 1TB', '160.000', '2.000', '80.00'],
        ['10', 'Webcam HD Pro', '140.000', '1.400', '100.00']
    ]
    
    product_table = Table(product_data, colWidths=[0.5*inch, 2*inch, 1*inch, 1*inch, 1*inch])
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(product_table)
    story.append(Spacer(1, 20))
    
    # Dritte Tabelle: Kundenanalyse
    story.append(Paragraph("Kundenanalyse nach Altersgruppen", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    customer_data = [
        ['Altersgruppe', 'Kunden', 'Umsatz €', 'Ø Bestellung €'],
        ['18-25', '15.500', '185.000', '11.94'],
        ['26-35', '28.300', '452.800', '16.00'],
        ['36-45', '22.100', '442.000', '20.00'],
        ['46-55', '18.800', '376.000', '20.00'],
        ['56-65', '12.400', '186.000', '15.00'],
        ['65+', '8.200', '98.400', '12.00'],
        ['Gesamt', '105.300', '1.740.200', '16.52']
    ]
    
    customer_table = Table(customer_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1.5*inch])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(customer_table)
    
    doc.build(story)
    return filename

def create_large_pdf():
    """Erstellt großes PDF mit mehreren Seiten"""
    filename = "05_large_handbuch.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Titel
    story.append(Paragraph("Benutzerhandbuch: RAG-System Integration", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    chapters = [
        ("1. Einführung", [
            "Das RAG-System (Retrieval-Augmented Generation) stellt eine moderne Lösung für intelligente Dokumentenverarbeitung und semantische Suche dar. Dieses Handbuch führt Sie durch alle Aspekte der Installation, Konfiguration und Nutzung des Systems.",
            "RAG-Systeme kombinieren die Vorteile von vortrainierten Sprachmodellen mit der Möglichkeit, spezifische Dokumente und Datenquellen zu durchsuchen. Dies ermöglicht präzise und kontextuelle Antworten basierend auf Ihren eigenen Dokumenten.",
            "Die wichtigsten Komponenten des Systems umfassen: Document Processing Pipeline, Embedding Generation, Vector Storage, Retrieval Engine und Query Processing. Jede Komponente ist modular aufgebaut und kann individuell konfiguriert werden."
        ]),
        
        ("2. Installation und Setup", [
            "Bevor Sie mit der Installation beginnen, stellen Sie sicher, dass Ihr System die Mindestanforderungen erfüllt: Python 3.8+, mindestens 8GB RAM, 50GB freier Speicherplatz.",
            "Installieren Sie zunächst die erforderlichen Dependencies: pip install rag-system torch transformers sentence-transformers chromadb fastapi uvicorn. Für GPU-Unterstützung installieren Sie zusätzlich: pip install torch[cuda].",
            "Erstellen Sie eine Konfigurationsdatei config.yaml mit Ihren spezifischen Einstellungen. Wichtige Parameter sind: chunk_size (empfohlen: 512), overlap_ratio (empfohlen: 0.1), embedding_model und vector_database_path.",
            "Starten Sie das System mit: python -m rag_system start --config config.yaml. Das System wird automatisch auf Port 8000 gestartet und ist unter http://localhost:8000 erreichbar."
        ]),
        
        ("3. Dokumentenverarbeitung", [
            "Der erste Schritt bei der Nutzung des RAG-Systems ist das Hochladen und Verarbeiten Ihrer Dokumente. Das System unterstützt verschiedene Dateiformate: PDF, DOCX, TXT, HTML und Markdown.",
            "Beim Upload werden Dokumente automatisch in kleinere Textabschnitte (Chunks) aufgeteilt. Die optimale Chunk-Größe liegt zwischen 300-800 Zeichen, um ein gutes Verhältnis zwischen Kontext und Präzision zu gewährleisten.",
            "Für jedes Chunk wird ein Embedding-Vektor generiert, der die semantische Bedeutung des Textes repräsentiert. Diese Vektoren werden in einer Vektordatenbank gespeichert für schnelle Ähnlichkeitssuchen.",
            "Metadaten wie Dokumententitel, Autor, Erstellungsdatum und Kategorien werden extrahiert und mit den Chunks verknüpft. Dies ermöglicht gefilterte Suchen nach spezifischen Kriterien."
        ]),
        
        ("4. Suche und Retrieval", [
            "Die semantische Suche erfolgt über die API-Endpoints oder die Web-Oberfläche. Geben Sie Ihre Frage in natürlicher Sprache ein - das System findet automatisch die relevantesten Dokumentenabschnitte.",
            "Der Retrieval-Prozess umfasst mehrere Schritte: Query Embedding Generation, Vector Similarity Search, Reranking der Ergebnisse und Context Assembly für die finale Antwortgenerierung.",
            "Sie können die Suchparameter anpassen: max_results (Anzahl der Ergebnisse), similarity_threshold (Mindestähnlichkeit), filters (Dokumentfilter) und rerank_enabled (Ergebnis-Reranking).",
            "Für komplexe Anfragen nutzen Sie die erweiterte Suchsyntax mit Booleschen Operatoren, Phrasensuche und Feldspezifikationen. Beispiel: 'machine learning AND (neural networks OR deep learning)'"
        ]),
        
        ("5. API-Integration", [
            "Das RAG-System bietet eine umfassende REST-API für die Integration in bestehende Anwendungen. Die API folgt OpenAPI 3.0 Standards und bietet automatische Dokumentation unter /docs.",
            "Wichtige Endpoints: POST /documents/upload (Dokument hochladen), GET /documents (Dokumente auflisten), POST /search (Semantische Suche), DELETE /documents/{id} (Dokument löschen).",
            "Für die Authentifizierung verwenden Sie API-Keys, die in der Konfiguration definiert werden. Jeder Request muss den Header 'X-API-Key' enthalten. Rate-Limiting ist standardmäßig auf 100 Requests pro Minute gesetzt.",
            "Die API unterstützt sowohl synchrone als auch asynchrone Verarbeitung. Für große Dokumente verwenden Sie den asynchronen Upload-Endpoint, der eine Job-ID zurückgibt zur Statusabfrage."
        ]),
        
        ("6. Monitoring und Wartung", [
            "Das System bietet umfassende Monitoring-Features über das Dashboard unter /admin. Hier finden Sie Statistiken zu Dokumentenanzahl, Speicherverbrauch, Query-Performance und Systemauslastung.",
            "Wichtige Metriken: Durchschnittliche Query-Latenz, Embedding-Generierung pro Minute, Cache-Hit-Rate und Speicherverbrauch der Vektordatenbank. Alerting ist für kritische Schwellwerte konfigurierbar.",
            "Regelmäßige Wartungsaufgaben umfassen: Index-Optimierung (wöchentlich), Backup der Vektordatenbank (täglich), Log-Rotation (täglich) und Performance-Tuning basierend auf Usage-Patterns.",
            "Für Backup und Disaster Recovery exportieren Sie regelmäßig die Vektordatenbank und Konfigurationsdateien. Der Export-Befehl: python -m rag_system export --output backup_folder"
        ]),
        
        ("7. Troubleshooting", [
            "Bei Performance-Problemen prüfen Sie zuerst die Systemressourcen: CPU, RAM und Festplatten-I/O. Das RAG-System ist speicherintensiv - mindestens 8GB RAM werden empfohlen.",
            "Häufige Probleme: Langsame Suchzeiten (Index-Rebuild erforderlich), hoher Speicherverbrauch (Chunk-Size reduzieren), schlechte Suchqualität (Embedding-Model wechseln).",
            "Für Debugging aktivieren Sie das Debug-Logging: python -m rag_system start --log-level DEBUG. Logs werden in logs/rag_system.log gespeichert.",
            "Bei Problemen mit der Dokumentenverarbeitung prüfen Sie die unterstützten Dateiformate und Größenbeschränkungen. Maximale Dateigröße: 100MB pro Dokument."
        ])
    ]
    
    for chapter_title, paragraphs in chapters:
        story.append(Paragraph(chapter_title, styles['Heading1']))
        story.append(Spacer(1, 16))
        
        for paragraph in paragraphs:
            story.append(Paragraph(paragraph, styles['Normal']))
            story.append(Spacer(1, 12))
        
        story.append(PageBreak())
    
    doc.build(story)
    return filename

def create_code_pdf():
    """Erstellt PDF mit Code-Beispielen"""
    filename = "06_code_documentation.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Code Style definieren
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leftIndent=20,
        backgroundColor=colors.lightgrey,
        borderWidth=1,
        borderColor=colors.black,
        borderPadding=5
    )
    
    story = []
    
    # Titel
    story.append(Paragraph("API-Dokumentation mit Code-Beispielen", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    # Python Beispiel
    story.append(Paragraph("Python Integration", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    python_code = """
from rag_system import RAGClient
import asyncio

async def main():
    client = RAGClient(
        base_url="http://localhost:8000",
        api_key="your-api-key"
    )
    
    # Dokument hochladen
    with open("document.pdf", "rb") as f:
        result = await client.upload_document(
            file=f,
            metadata={"category": "technical"}
        )
    
    print(f"Document ID: {result.document_id}")
    
    # Semantische Suche
    search_results = await client.search(
        query="How does machine learning work?",
        max_results=5
    )
    
    for result in search_results:
        print(f"Score: {result.similarity_score}")
        print(f"Content: {result.content[:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
"""
    
    story.append(Paragraph(python_code, code_style))
    story.append(Spacer(1, 20))
    
    # JavaScript Beispiel
    story.append(Paragraph("JavaScript/Node.js Integration", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    js_code = """
const axios = require('axios');
const fs = require('fs');

class RAGClient {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }
    
    async uploadDocument(filePath, metadata = {}) {
        const formData = new FormData();
        formData.append('file', fs.createReadStream(filePath));
        formData.append('metadata', JSON.stringify(metadata));
        
        const response = await axios.post(
            `${this.baseUrl}/documents/upload`,
            formData,
            {
                headers: {
                    'X-API-Key': this.apiKey,
                    'Content-Type': 'multipart/form-data'
                }
            }
        );
        
        return response.data;
    }
    
    async search(query, maxResults = 10) {
        const response = await axios.post(
            `${this.baseUrl}/search`,
            {
                query: query,
                max_results: maxResults
            },
            {
                headers: {
                    'X-API-Key': this.apiKey,
                    'Content-Type': 'application/json'
                }
            }
        );
        
        return response.data.results;
    }
}

// Verwendung
const client = new RAGClient(
    'http://localhost:8000', 
    'your-api-key'
);

client.uploadDocument('./document.pdf')
    .then(result => console.log('Uploaded:', result))
    .catch(err => console.error('Error:', err));
"""
    
    story.append(Paragraph(js_code, code_style))
    story.append(Spacer(1, 20))
    
    # curl Beispiele
    story.append(Paragraph("REST API mit curl", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    curl_examples = """
# Dokument hochladen
curl -X POST http://localhost:8000/documents/upload \\
  -H "X-API-Key: your-api-key" \\
  -F "file=@document.pdf" \\
  -F 'metadata={"category":"research"}'

# Semantische Suche
curl -X POST http://localhost:8000/search \\
  -H "X-API-Key: your-api-key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "machine learning algorithms",
    "max_results": 5,
    "similarity_threshold": 0.7
  }'

# Dokument löschen
curl -X DELETE http://localhost:8000/documents/123 \\
  -H "X-API-Key: your-api-key"

# Systemstatus abfragen
curl -X GET http://localhost:8000/health \\
  -H "X-API-Key: your-api-key"
"""
    
    story.append(Paragraph(curl_examples, code_style))
    
    doc.build(story)
    return filename

def main():
    """Erstellt alle Test-PDF-Dokumente"""
    print("📁 Erstelle Test-PDF-Dokumente für Chunking-Evaluierung...")
    
    # Verzeichnis erstellen falls nicht vorhanden
    os.makedirs(".", exist_ok=True)
    
    pdfs = []
    
    try:
        print("1️⃣ Erstelle Mini-PDF (Kündigung)...")
        pdfs.append(create_mini_pdf())
        
        print("2️⃣ Erstelle Small-PDF (Bewerbung)...")
        pdfs.append(create_small_pdf())
        
        print("3️⃣ Erstelle Medium-PDF (Projektplan)...")
        pdfs.append(create_medium_pdf())
        
        print("4️⃣ Erstelle Table-PDF (Verkaufsbericht)...")
        pdfs.append(create_table_pdf())
        
        print("5️⃣ Erstelle Large-PDF (Handbuch)...")
        pdfs.append(create_large_pdf())
        
        print("6️⃣ Erstelle Code-PDF (API-Dokumentation)...")
        pdfs.append(create_code_pdf())
        
        print("\n✅ Alle Test-PDFs erfolgreich erstellt:")
        for i, pdf in enumerate(pdfs, 1):
            file_size = os.path.getsize(pdf) / 1024  # KB
            print(f"   {i}. {pdf} ({file_size:.1f} KB)")
        
        print(f"\n🎯 Evaluierungs-Szenarien:")
        print(f"   • Mini-PDF: Tests Single-Chunk Fallback")
        print(f"   • Small-PDF: Tests optimale kleine Dokumente") 
        print(f"   • Medium-PDF: Tests strukturierte Dokumente")
        print(f"   • Table-PDF: Tests Tabellen-Intelligenz")
        print(f"   • Large-PDF: Tests Multi-Page Chunking")
        print(f"   • Code-PDF: Tests Code-spezifisches Chunking")
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der PDFs: {e}")
        print("💡 Stellen Sie sicher, dass reportlab installiert ist: pip install reportlab")

if __name__ == "__main__":
    main()