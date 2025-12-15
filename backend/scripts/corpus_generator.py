"""
Corpus Generator
Generates a realistic enterprise document corpus for RAG testing.
Includes 50+ files: PDFs, Markdowns, Text files.
"""

import os
import random
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime, timedelta

CORPUS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_corpus_large"
)

CATEGORIES = {
    "HR": ["Richtlinie", "Onboarding", "Benefits", "Urlaub"],
    "IT": ["Security", "VPN", "Hardware", "Software_Katalog"],
    "Projects": ["Streamworks_Migration", "Cloud_Native_Initiative", "Legacy_Shutdown"],
    "MeetingNotes": ["Q1_Planning", "Weekly_Sync", "Retrospective"],
    "Specs": ["API_Reference", "Database_Schema", "Architecture_Decision_Record"],
}

# Templates for realistic content generation
TEMPLATES = {
    "policy": """
    # {title}
    Status: {status}
    Gültig ab: {date}
    
    ## 1. Zweck
    Diese Richtlinie regelt den Umgang mit {topic} im Unternehmen.
    
    ## 2. Geltungsbereich
    Gilt für alle Mitarbeiter der Streamworks GmbH.
    
    ## 3. Details
    {details}
    
    ## 4. Ausnahmen
    Ausnahmen bedürfen der schriftlichen Genehmigung durch {approver}.
    """,
    "tech_spec": """
    Technical Specification: {title}
    Version: {version}
    Author: {author}
    
    1. Overview
    ----------------
    The {component} is designed to handle {load} requests per second.
    It connects to {dependency} using protocol {protocol}.
    
    2. Configuration
    ----------------
    Key configuration parameters:
    - TIMEOUT_MS: {timeout}
    - MAX_RETRIES: {retries}
    - ENABLE_FEATURE_X: {feature_flag}
    
    3. Known Issues
    ----------------
    - Issue #{issue_id}: {issue_desc}
    """,
}


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def generate_pdf(filepath, title, content):
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, title)

    c.setFont("Helvetica", 12)
    text_object = c.beginText(50, height - 80)

    for line in content.split("\n"):
        # Simple wrapping
        if len(line) > 80:
            chunks = [line[i : i + 80] for i in range(0, len(line), 80)]
            for chunk in chunks:
                text_object.textLine(chunk)
        else:
            text_object.textLine(line)

    c.drawText(text_object)
    c.save()


def generate_corpus():
    print(f"🏭 Generating corpus in {CORPUS_DIR}...")
    ensure_dir(CORPUS_DIR)

    files_metadata = []

    # 1. Generate HR Policies (PDFs)
    print("   - Generating HR Policies...")
    for i in range(10):
        topic = random.choice(CATEGORIES["HR"])
        title = f"HR_{topic}_v{2024 + i}"
        filename = f"{title}.pdf"

        # Specific hidden fact for later testing
        special_detail = ""
        if i == 5:
            special_detail = "Das 'Remote-First' Programm erlaubt 100% Homeoffice für Level 3 Engineers."

        content = f"""
        Offizielle HR Richtlinie: {topic}
        Dokument-ID: HR-{1000 + i}
        
        Alle Mitarbeiter haben Anspruch auf {25 + i} Tage Urlaub.
        Überstunden müssen bis zum {15 + i}. des Folgemonats abgebaut werden.
        
        {special_detail}
        
        Kontakt: hr@streamworks.internal
        """

        generate_pdf(os.path.join(CORPUS_DIR, filename), title, content)
        files_metadata.append({"file": filename, "type": "pdf", "category": "HR"})

    # 2. Generate IT Docs (Markdown)
    print("   - Generating IT Documentation...")
    for i in range(15):
        topic = str(random.choice(CATEGORIES["IT"]))
        filename = f"IT_{topic}_{i}.md"

        # Trap: Conflicting versions
        version = "1.0" if i < 10 else "2.0 (DRAFT)"
        timeout_val = "30s" if i < 10 else "120s"

        content = TEMPLATES["policy"].format(
            title=f"IT Standard: {topic}",
            status="Active" if i < 10 else "Draft",
            date="2025-01-01",
            topic=topic,
            details=f"Der Standard-Timeout für {topic}-Verbindungen beträgt {timeout_val}. Version {version}.",
            approver="CTO",
        )

        with open(os.path.join(CORPUS_DIR, filename), "w") as f:
            f.write(content)
        files_metadata.append({"file": filename, "type": "md", "category": "IT"})

    # 3. Generate Technical Specs (Text)
    print("   - Generating Tech Specs...")
    for i in range(15):
        topic = str(random.choice(CATEGORIES["Specs"]))
        filename = f"SPEC_{topic}_{i}.txt"

        content = TEMPLATES["tech_spec"].format(
            title=f"{topic} Implementation Guide",
            version=f"3.{i}",
            author=f"Dev_{i}",
            component=topic,
            load=1000 + (i * 100),
            dependency=f"Service_{i}",
            protocol="gRPC" if i % 2 == 0 else "REST",
            timeout=5000 + (i * 10),
            retries=3,
            feature_flag="true",
            issue_id=400 + i,
            issue_desc="Memory leak in high load scenarios",
        )

        with open(os.path.join(CORPUS_DIR, filename), "w") as f:
            f.write(content)
        files_metadata.append({"file": filename, "type": "txt", "category": "Specs"})

    # 4. Generate Project Files (JSON)
    print("   - Generating Project Metadata...")
    for i in range(10):
        project = str(random.choice(CATEGORIES["Projects"]))
        filename = f"PROJ_{project}_{i}.json"

        data = {
            "project_name": project,
            "id": f"PRJ-{i}",
            "budget": 50000 + (i * 10000),
            "team_size": random.randint(3, 15),
            "status": random.choice(["green", "yellow", "red"]),
            "notes": f"Critical milestone due on {datetime.now().date() + timedelta(days=i * 10)}",
        }

        with open(os.path.join(CORPUS_DIR, filename), "w") as f:
            json.dump(data, f, indent=2)
        files_metadata.append(
            {"file": filename, "type": "json", "category": "Projects"}
        )

    # 5. Generate THE MONSTER (80 Page Manual)
    print("   - Generating 80-page Enterprise Manual...")
    manual_path = os.path.join(CORPUS_DIR, "Streamworks_Enterprise_Manual_v2025.pdf")
    c = canvas.Canvas(manual_path, pagesize=letter)
    width, height = letter

    # Page 1: Title
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2, height / 2, "Global Architecture Guide 2025")
    c.setFont("Helvetica", 20)
    c.drawCentredString(width / 2, height / 2 - 50, "CONFIDENTIAL")
    c.showPage()

    # Pages 2-79: Filler + Hidden Needles
    for p in range(2, 81):
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, f"Chapter {p}: Enterprise Scalability (Page {p})")

        c.setFont("Helvetica", 10)
        text = c.beginText(50, height - 80)

        # Filler content
        content_block = (
            """
        The scalability of the system depends on the underlying standardized protocols.
        We utilize a distributed mesh network of agents to ensure high availability.
        Latency is minimized through edge computing paradigms and proactive caching.
        """
            * 10
        )

        # Inject Needle on Page 42
        if p == 42:
            content_block += "\n\nCRITICAL CONFIGURATION: The master node DB connection pool must be set to exactly 1337 connections for cluster sizes > 500 nodes.\n\n"

        # Inject Needle on Page 75
        if p == 75:
            content_block += "\n\nDEPRECATION NOTICE: The 'LegacyAuth' module is strictly forbidden in production since Patch 4.5.2.\n\n"

        for line in content_block.split("\n"):
            if len(line.strip()) > 0:
                text.textLine(line.strip())

        c.drawText(text)
        c.showPage()

    c.save()
    files_metadata.append(
        {
            "file": "Streamworks_Enterprise_Manual_v2025.pdf",
            "type": "pdf",
            "category": "Docs",
        }
    )

    print(f"✅ Generated {len(files_metadata)} documents including the Monster Manual.")
    return len(files_metadata)


if __name__ == "__main__":
    generate_corpus()
