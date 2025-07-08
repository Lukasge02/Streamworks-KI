"""
TXT to Markdown Converter für optimierte RAG-Performance
"""
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TxtToMdConverter:
    """Konvertiert TXT-Dateien zu optimierten Markdown-Dateien"""
    
    def __init__(self):
        self.streamworks_terms = {
            "batch": "Batch-Verarbeitung",
            "stream": "Stream-Verarbeitung", 
            "job": "Verarbeitungsauftrag",
            "schedule": "Zeitplanung",
            "cron": "Cron-Ausdruck",
            "monitoring": "Überwachung",
            "pipeline": "Verarbeitungspipeline",
            "xml": "XML-Konfiguration",
            "api": "API-Schnittstelle",
            "database": "Datenbank",
            "backup": "Datensicherung",
            "import": "Datenimport",
            "export": "Datenexport",
            "powershell": "PowerShell-Skript",
            "csv": "CSV-Datenverarbeitung",
            "error": "Fehlerbehandlung",
            "config": "Konfiguration",
            "log": "Protokollierung",
            "server": "Server-System",
            "client": "Client-Anwendung"
        }
    
    async def convert_txt_to_md(self, txt_file_path: Path, optimized_dir: Path) -> Path:
        """
        Konvertiert TXT-Datei zu optimierter Markdown-Datei
        
        Args:
            txt_file_path: Pfad zur TXT-Datei
            optimized_dir: Verzeichnis für optimierte MD-Datei
            
        Returns:
            Path zur generierten MD-Datei
        """
        try:
            logger.info(f"🔄 Konvertiere TXT zu MD: {txt_file_path.name}")
            
            # Lese TXT-Datei
            with open(txt_file_path, 'r', encoding='utf-8') as f:
                txt_content = f.read()
            
            # Konvertiere zu Markdown
            md_content = await self._convert_content(txt_content, txt_file_path.name)
            
            # Erstelle MD-Datei im optimized Verzeichnis
            md_filename = txt_file_path.stem + "_optimized.md"
            md_file_path = optimized_dir / md_filename
            
            # Stelle sicher, dass das Verzeichnis existiert
            optimized_dir.mkdir(parents=True, exist_ok=True)
            
            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"✅ MD-Datei erstellt: {md_file_path}")
            return md_file_path
            
        except Exception as e:
            logger.error(f"❌ TXT zu MD Konvertierung fehlgeschlagen: {e}")
            raise
    
    async def _convert_content(self, txt_content: str, filename: str) -> str:
        """Konvertiert TXT-Inhalt zu strukturiertem Markdown"""
        
        # Basis-Markdown-Struktur
        title = self._generate_title(filename)
        now_str = datetime.now().strftime('%d.%m.%Y %H:%M')
        md_content = f"""# {title}

**Automatisch generiert aus**: {filename}  
**Konvertiert am**: {now_str}  
**Typ**: StreamWorks-Dokumentation

---

"""
        
        # Verarbeite Inhalt
        processed_content = await self._process_content(txt_content)
        
        # Strukturiere Inhalt
        structured_content = await self._structure_content(processed_content)
        
        # Füge zusammen
        md_content += structured_content
        
        # Füge Metadaten hinzu
        md_content += await self._add_metadata(txt_content)
        
        return md_content
    
    def _generate_title(self, filename: str) -> str:
        """Generiert sinnvollen Titel aus Dateiname"""
        
        # Entferne UUID-Präfix und Dateiendung
        title = filename.replace('.txt', '')
        
        # Entferne UUID-Pattern (8-4-4-4-12 Zeichen)
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}_'
        title = re.sub(uuid_pattern, '', title)
        
        # Ersetze Unterstriche und Bindestriche durch Leerzeichen
        title = title.replace('_', ' ').replace('-', ' ')
        
        # Erkenne StreamWorks-Begriffe
        for term, german in self.streamworks_terms.items():
            if term in title.lower():
                title = title.replace(term, german)
        
        # Erste Buchstaben groß
        title = ' '.join(word.capitalize() for word in title.split())
        
        return title if title else "StreamWorks Dokumentation"
    
    async def _process_content(self, content: str) -> str:
        """Verarbeitet den TXT-Inhalt für bessere Struktur"""
        
        # Bereinige Inhalt
        processed = content.strip()
        
        # Entferne übermäßige Leerzeilen
        processed = re.sub(r'\n\s*\n\s*\n+', '\n\n', processed)
        
        # Erkenne und markiere StreamWorks-Begriffe (nur erste Erwähnung)
        marked_terms = set()
        for term, german in self.streamworks_terms.items():
            if term not in marked_terms and term in processed.lower():
                # Finde erste Erwähnung und markiere sie
                pattern = r'\b' + re.escape(term) + r'\b'
                match = re.search(pattern, processed, re.IGNORECASE)
                if match:
                    replacement = f'**{match.group()}** ({german})'
                    processed = processed[:match.start()] + replacement + processed[match.end():]
                    marked_terms.add(term)
        
        return processed
    
    async def _structure_content(self, content: str) -> str:
        """Strukturiert den Inhalt mit Markdown-Elementen"""
        
        lines = content.split('\n')
        structured_lines = []
        
        in_code_block = False
        current_list_level = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Leere Zeilen beibehalten
            if not stripped:
                if in_code_block:
                    structured_lines.append('```')
                    structured_lines.append('')
                    in_code_block = False
                else:
                    structured_lines.append('')
                current_list_level = 0
                continue
            
            # Erkenne Code-Blöcke
            if self._is_code_line(stripped):
                if not in_code_block:
                    structured_lines.append('```')
                    in_code_block = True
                structured_lines.append(line)
                continue
            
            # Schließe Code-Block wenn nötig
            if in_code_block and not self._is_code_line(stripped):
                structured_lines.append('```')
                structured_lines.append('')
                in_code_block = False
            
            # Erkenne Überschriften
            if self._is_heading(stripped):
                heading_text = self._format_heading(stripped)
                level = self._determine_heading_level(stripped, i, lines)
                structured_lines.append(f'\n{"#" * level} {heading_text}\n')
                current_list_level = 0
                continue
            
            # Erkenne Listen
            if self._is_list_item(stripped):
                formatted_item = self._format_list_item(stripped)
                structured_lines.append(formatted_item)
                current_list_level = 1
                continue
            
            # Erkenne Definitionen
            if self._is_definition(stripped):
                formatted_def = self._format_definition(stripped)
                structured_lines.append(formatted_def)
                current_list_level = 0
                continue
            
            # Erkenne wichtige Hinweise
            if self._is_important(stripped):
                formatted_note = self._format_important(stripped)
                structured_lines.append(formatted_note)
                current_list_level = 0
                continue
            
            # Erkenne Q&A Pattern
            if self._is_question(stripped):
                formatted_qa = self._format_question(stripped)
                structured_lines.append(formatted_qa)
                current_list_level = 0
                continue
            
            # Normale Zeile
            structured_lines.append(line)
            current_list_level = 0
        
        # Schließe offene Code-Blöcke
        if in_code_block:
            structured_lines.append('```')
        
        return '\n'.join(structured_lines)
    
    def _is_code_line(self, line: str) -> bool:
        """Erkennt Code-Zeilen"""
        code_indicators = [
            r'<?xml', r'<stream', r'<job', r'<schedule',
            r'curl ', r'http[s]?://', 
            r'python ', r'pip ', r'npm ',
            r'SELECT ', r'INSERT ', r'UPDATE ',
            r'function ', r'class ', r'def ',
            r'^\s*\w+\s*=\s*.+',  # Zuweisungen
            r'^\s*\w+\.\w+',      # Objekt-Methoden
            r'powershell', r'ps1', r'\$\w+',  # PowerShell
            r'^\s*[A-Z_]+\s*=',   # Umgebungsvariablen
        ]
        
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in code_indicators)
    
    def _is_heading(self, line: str) -> bool:
        """Erkennt Überschriften"""
        heading_patterns = [
            r'^[A-Z][A-Z\s]+:$',      # ÜBERSCHRIFT:
            r'^[A-Z][^.!?]{10,}:$',   # Längere Überschrift:
            r'^\d+\.\s+[A-Z]',        # 1. Überschrift
            r'^[A-Z][A-Z\s]{8,}$',    # LANGE ÜBERSCHRIFT
            r'^={3,}.*={3,}$',        # ===ÜBERSCHRIFT===
            r'^-{3,}.*-{3,}$',        # ---ÜBERSCHRIFT---
        ]
        
        return any(re.match(pattern, line) for pattern in heading_patterns)
    
    def _determine_heading_level(self, line: str, index: int, all_lines: List[str]) -> int:
        """Bestimmt die Überschrifts-Ebene"""
        
        # Level 1: Sehr große Überschriften
        if re.match(r'^[A-Z][A-Z\s]{10,}:?$', line) or re.match(r'^={3,}.*={3,}$', line):
            return 2
        
        # Level 2: Nummerierte Hauptüberschriften  
        if re.match(r'^\d+\.\s+[A-Z]', line):
            return 3
        
        # Level 3: Normale Überschriften
        return 3
    
    def _format_heading(self, line: str) -> str:
        """Formatiert Überschriften"""
        # Entferne Doppelpunkte, Gleichheitszeichen und Nummerierung
        heading = re.sub(r'^\d+\.\s*', '', line)
        heading = heading.rstrip(':')
        heading = re.sub(r'^[=\-]{3,}\s*', '', heading)
        heading = re.sub(r'\s*[=\-]{3,}$', '', heading)
        
        # Füge Emojis für StreamWorks-Begriffe hinzu
        emoji_map = {
            'fehler': '❌',
            'error': '❌', 
            'problem': '⚠️',
            'lösung': '✅',
            'config': '⚙️',
            'konfiguration': '⚙️',
            'api': '🔗',
            'schedule': '⏰',
            'zeitplan': '⏰',
            'batch': '📦',
            'stream': '🌊',
            'monitoring': '📊',
            'überwachung': '📊',
            'backup': '💾',
            'import': '📥',
            'export': '📤'
        }
        
        heading_lower = heading.lower()
        for term, emoji in emoji_map.items():
            if term in heading_lower:
                heading = f"{emoji} {heading}"
                break
        
        return heading.strip()
    
    def _is_list_item(self, line: str) -> bool:
        """Erkennt Listen-Elemente"""
        list_patterns = [
            r'^-\s+',           # - Item
            r'^\*\s+',          # * Item
            r'^\d+\.\s+',       # 1. Item
            r'^[a-zA-Z]\.\s+',  # a. Item
            r'^[a-zA-Z]\)\s+',  # a) Item
            r'^\s*•\s+',        # • Item
        ]
        
        return any(re.match(pattern, line) for pattern in list_patterns)
    
    def _format_list_item(self, line: str) -> str:
        """Formatiert Listen-Elemente"""
        # Standardisiere zu Markdown-Liste
        if not line.strip().startswith('- '):
            # Entferne andere Marker und ersetze durch -
            clean_line = re.sub(r'^\s*[\*\d+\w•]+[\.\)]\s*', '', line.strip())
            return f"- {clean_line}"
        
        return line
    
    def _is_definition(self, line: str) -> bool:
        """Erkennt Definitionen"""
        definition_patterns = [
            r'^[A-Z][^:]{2,20}:\s*[a-z]',    # Begriff: definition
            r'^[A-Z][^-]{2,20}\s*-\s*[a-z]', # Begriff - definition
        ]
        
        return any(re.match(pattern, line) for pattern in definition_patterns)
    
    def _format_definition(self, line: str) -> str:
        """Formatiert Definitionen"""
        # Teile Begriff und Definition
        if ':' in line:
            parts = line.split(':', 1)
            term = parts[0].strip()
            definition = parts[1].strip()
            return f"**{term}**: {definition}"
        elif ' - ' in line:
            parts = line.split(' - ', 1)
            term = parts[0].strip()
            definition = parts[1].strip()
            return f"**{term}**: {definition}"
        
        return line
    
    def _is_important(self, line: str) -> bool:
        """Erkennt wichtige Hinweise"""
        important_keywords = [
            'wichtig', 'achtung', 'hinweis', 'warnung', 'beachten',
            'important', 'note', 'warning', 'attention', 'caution',
            'tipp', 'tip', 'info'
        ]
        
        return any(keyword in line.lower() for keyword in important_keywords)
    
    def _format_important(self, line: str) -> str:
        """Formatiert wichtige Hinweise"""
        line_lower = line.lower()
        
        if any(word in line_lower for word in ['warnung', 'warning', 'achtung']):
            return f"> ⚠️ **Warnung**: {line}"
        elif any(word in line_lower for word in ['tipp', 'tip']):
            return f"> 💡 **Tipp**: {line}"
        elif any(word in line_lower for word in ['hinweis', 'note', 'info']):
            return f"> ℹ️ **Hinweis**: {line}"
        else:
            return f"> **💡 Wichtig**: {line}"
    
    def _is_question(self, line: str) -> bool:
        """Erkennt Fragen (Q&A Format)"""
        question_patterns = [
            r'^F:\s+',     # F: Frage
            r'^Q:\s+',     # Q: Question
            r'^Frage:\s+', # Frage: 
            r'.*\?$',      # Endet mit ?
        ]
        
        return any(re.match(pattern, line) for pattern in question_patterns)
    
    def _format_question(self, line: str) -> str:
        """Formatiert Fragen"""
        # Entferne Q:/F: Präfixe und formatiere als Überschrift
        question = re.sub(r'^[FQ]:\s*', '', line)
        question = re.sub(r'^Frage:\s*', '', question)
        
        return f"### ❓ {question}"
    
    async def _add_metadata(self, original_content: str) -> str:
        """Fügt Metadaten für bessere RAG-Performance hinzu"""
        
        # Extrahiere Schlüsselwörter
        keywords = self._extract_keywords(original_content)
        
        # Erkenne Themen
        topics = self._detect_topics(original_content)
        
        # Schätze Komplexität
        complexity = self._estimate_complexity(original_content)
        
        # Erkenne Sprache
        language = self._detect_language(original_content)
        
        # Berechne Statistiken
        word_count = len(original_content.split())
        line_count = len(original_content.split('\n'))
        reading_time = max(1, word_count // 200)
        
        # Format timestamp
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        metadata = f"""

---

## 📊 Dokumenten-Metadaten

### 🏷️ Schlüsselwörter
{', '.join(keywords) if keywords else 'Keine spezifischen Schlüsselwörter erkannt'}

### 🎯 Themen
{', '.join(topics)}

### 📈 Komplexität
{complexity}

### 🌐 Sprache
{language}

### 🔍 Suchbegriffe
{self._generate_search_terms(keywords, topics)}

### 📏 Statistiken
- **Wortanzahl**: {word_count} Wörter
- **Zeilen**: {line_count} Zeilen
- **Geschätzte Lesezeit**: {reading_time} Minuten

---

*Dieses Dokument wurde automatisch für StreamWorks-KI optimiert - {timestamp}*
"""
        
        return metadata
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extrahiert Schlüsselwörter aus dem Inhalt"""
        
        keywords = set()
        content_lower = content.lower()
        
        # StreamWorks-Begriffe
        for term in self.streamworks_terms.keys():
            if term in content_lower:
                keywords.add(term)
        
        # Technische Begriffe
        tech_terms = [
            'xml', 'api', 'database', 'server', 'client', 'config', 'log',
            'powershell', 'script', 'automation', 'workflow', 'data',
            'file', 'process', 'system', 'service', 'application'
        ]
        for term in tech_terms:
            if term in content_lower:
                keywords.add(term)
        
        # Häufige Wörter (vereinfacht)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content_lower)
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Häufigste Wörter (außer Stopwörter)
        stopwords = {
            'und', 'der', 'die', 'das', 'ist', 'ein', 'eine', 'für', 'mit', 
            'auf', 'von', 'zu', 'im', 'am', 'an', 'bei', 'nach', 'vor', 
            'über', 'unter', 'zwischen', 'wird', 'werden', 'kann', 'sind',
            'have', 'this', 'that', 'with', 'from', 'they', 'been', 'said'
        }
        frequent_words = [
            word for word, freq in word_freq.items() 
            if freq > 2 and word not in stopwords and len(word) > 3
        ][:5]
        
        keywords.update(frequent_words)
        
        return sorted(list(keywords))
    
    def _detect_topics(self, content: str) -> List[str]:
        """Erkennt Themen im Inhalt"""
        
        topics = []
        content_lower = content.lower()
        
        topic_keywords = {
            'Batch-Verarbeitung': ['batch', 'stapel', 'verarbeitung', 'job', 'prozess'],
            'Zeitplanung': ['schedule', 'zeitplan', 'cron', 'timer', 'automation'],
            'Monitoring': ['monitoring', 'überwachung', 'log', 'alert', 'protokoll'],
            'Konfiguration': ['config', 'einstellung', 'parameter', 'xml', 'setup'],
            'Troubleshooting': ['fehler', 'problem', 'lösung', 'debug', 'error'],
            'API-Integration': ['api', 'schnittstelle', 'rest', 'endpoint', 'service'],
            'Datenverarbeitung': ['daten', 'import', 'export', 'transformation', 'csv'],
            'PowerShell': ['powershell', 'script', 'ps1', 'cmdlet'],
            'Systemadministration': ['server', 'system', 'admin', 'installation', 'deployment'],
            'FAQ': ['frage', 'antwort', 'question', 'answer', 'hilfe']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)
        
        return topics if topics else ['Allgemeine Dokumentation']
    
    def _estimate_complexity(self, content: str) -> str:
        """Schätzt die Komplexität des Inhalts"""
        
        word_count = len(content.split())
        line_count = len(content.split('\n'))
        
        # Technische Indikatoren
        tech_indicators = ['xml', 'api', 'script', 'code', 'config', 'database']
        tech_score = sum(1 for indicator in tech_indicators if indicator in content.lower())
        
        # Komplexitäts-Score
        if word_count < 100 and tech_score < 2:
            return "Einfach (Grundlagen)"
        elif word_count < 500 and tech_score < 4:
            return "Mittel (Fortgeschritten)"
        else:
            return "Komplex (Experte)"
    
    def _detect_language(self, content: str) -> str:
        """Erkennt die Hauptsprache des Inhalts"""
        
        german_indicators = ['und', 'der', 'die', 'das', 'ist', 'für', 'mit', 'auf', 'von']
        english_indicators = ['and', 'the', 'for', 'with', 'from', 'that', 'this', 'have']
        
        german_count = sum(1 for word in german_indicators if word in content.lower())
        english_count = sum(1 for word in english_indicators if word in content.lower())
        
        if german_count > english_count:
            return "Deutsch"
        elif english_count > german_count:
            return "Englisch"
        else:
            return "Gemischt/Unbekannt"
    
    def _generate_search_terms(self, keywords: List[str], topics: List[str]) -> str:
        """Generiert erweiterte Suchbegriffe"""
        
        search_terms = set()
        
        # Keywords hinzufügen
        search_terms.update(keywords)
        
        # Themen hinzufügen
        search_terms.update([topic.lower().replace('-', ' ') for topic in topics])
        
        # Synonyme hinzufügen
        for keyword in keywords:
            if keyword in self.streamworks_terms:
                search_terms.add(self.streamworks_terms[keyword].lower())
        
        # Erweiterte Begriffe
        extended_terms = {
            'batch': ['stapelverarbeitung', 'massendaten'],
            'stream': ['datenstream', 'streaming'],
            'api': ['schnittstelle', 'webservice'],
            'config': ['konfiguration', 'einstellung'],
            'monitor': ['überwachung', 'monitoring'],
            'error': ['fehler', 'problem'],
            'schedule': ['zeitplan', 'planung']
        }
        
        for keyword in keywords:
            if keyword in extended_terms:
                search_terms.update(extended_terms[keyword])
        
        return ', '.join(sorted(search_terms)[:15])  # Limitiere auf 15 Begriffe

    async def convert_file(self, file_path: str) -> Optional[str]:
        """
        Convert TXT file to optimized Markdown (compatibility method for TrainingService)
        
        Args:
            file_path: Path to the TXT file
            
        Returns:
            Path to the generated MD file, or None if conversion failed
        """
        try:
            txt_path = Path(file_path)
            if not txt_path.exists():
                logger.error(f"TXT file not found: {file_path}")
                return None
            
            # Create optimized directory (correct path structure)
            # From: data/training_data/originals/help_data/file.txt
            # To:   data/training_data/optimized/help_data/file.md
            base_data_dir = txt_path.parent.parent.parent  # Go up to data/training_data/
            optimized_dir = base_data_dir / "optimized" / "help_data" 
            optimized_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert TXT to MD
            md_path = await self.convert_txt_to_md(txt_path, optimized_dir)
            
            logger.info(f"✅ TXT to MD conversion completed: {txt_path.name} → {md_path.name}")
            return str(md_path)
            
        except Exception as e:
            logger.error(f"❌ TXT to MD conversion failed for {file_path}: {e}")
            return None

# Global instance
txt_to_md_converter = TxtToMdConverter()