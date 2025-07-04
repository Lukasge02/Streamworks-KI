"""
Intelligent Search Service mit Synonym-Erweiterung für bessere RAG-Performance
"""
import logging
import re
from typing import Dict, List, Set
from datetime import datetime

logger = logging.getLogger(__name__)

class IntelligentSearch:
    """Intelligente Suchfunktion mit Synonym-Unterstützung"""
    
    def __init__(self):
        # Bidirektionale Synonyme für DE/EN StreamWorks-Begriffe
        self.synonyms = {
            "fehler": ["error", "problem", "issue", "bug", "störung", "defekt", "ausfall"],
            "error": ["fehler", "problem", "issue", "bug", "störung", "defekt"],
            "zeitplan": ["schedule", "cron", "timer", "planung", "timing", "automation"],
            "schedule": ["zeitplan", "cron", "timer", "planung", "timing", "automation"],
            "überwachung": ["monitoring", "log", "alert", "watch", "protokoll", "logging"],
            "monitoring": ["überwachung", "log", "alert", "watch", "protokoll", "logging"],
            "konfiguration": ["config", "setup", "einstellung", "parameter", "settings"],
            "config": ["konfiguration", "setup", "einstellung", "parameter", "settings"],
            "batch": ["stapel", "verarbeitung", "bulk", "masse", "job", "prozess"],
            "stapel": ["batch", "verarbeitung", "bulk", "masse", "job", "prozess"],
            "stream": ["datenstrom", "streaming", "pipeline", "flow", "datenfluss"],
            "datenstrom": ["stream", "streaming", "pipeline", "flow", "datenfluss"],
            "datenbank": ["database", "db", "sql", "tabelle", "speicher"],
            "database": ["datenbank", "db", "sql", "tabelle", "speicher"],
            "api": ["schnittstelle", "endpoint", "service", "webservice", "rest"],
            "schnittstelle": ["api", "endpoint", "service", "webservice", "rest"],
            "backup": ["sicherung", "datensicherung", "archiv", "kopie"],
            "sicherung": ["backup", "datensicherung", "archiv", "kopie"],
            "import": ["einlesen", "laden", "importieren", "datenimport"],
            "einlesen": ["import", "laden", "importieren", "datenimport"],
            "export": ["ausgabe", "exportieren", "speichern", "datenexport"],
            "ausgabe": ["export", "exportieren", "speichern", "datenexport"],
            "powershell": ["ps1", "cmdlet", "script", "automation", "windows"],
            "ps1": ["powershell", "cmdlet", "script", "automation", "windows"],
            "csv": ["komma", "tabelle", "excel", "daten", "datei"],
            "excel": ["csv", "tabelle", "xlsx", "daten", "datei"],
            "xml": ["markup", "konfiguration", "struktur", "format"],
            "markup": ["xml", "html", "struktur", "format"],
            "server": ["system", "host", "machine", "rechner"],
            "system": ["server", "host", "machine", "rechner"],
            "client": ["anwendung", "app", "benutzer", "frontend"],
            "anwendung": ["client", "app", "benutzer", "frontend"],
            "hilfe": ["help", "anleitung", "dokumentation", "guide", "faq"],
            "help": ["hilfe", "anleitung", "dokumentation", "guide", "faq"],
            "anleitung": ["tutorial", "guide", "howto", "manual", "hilfe"],
            "tutorial": ["anleitung", "guide", "howto", "manual", "hilfe"]
        }
        
        # Kontextuelle Begriffe für erweiterte Suche
        self.contextual_terms = {
            "streamworks": ["batch", "stream", "job", "schedule", "monitoring", "xml", "api"],
            "fehlerbehandlung": ["error", "exception", "try", "catch", "debug", "log"],
            "automatisierung": ["automation", "schedule", "cron", "batch", "script"],
            "datenverarbeitung": ["data", "processing", "import", "export", "csv", "xml"],
            "konfiguration": ["config", "setup", "parameter", "settings", "xml"],
            "überwachung": ["monitoring", "log", "alert", "status", "health"]
        }
    
    def expand_query(self, query: str) -> str:
        """
        Erweitert Query um Synonyme und kontextuelle Begriffe
        
        Args:
            query: Original-Suchquery
            
        Returns:
            Erweiterte Query mit Synonymen
        """
        try:
            logger.info(f"🔍 Erweitere Suchquery: '{query}'")
            
            # Normalisiere Query
            original_words = self._extract_words(query.lower())
            expanded_terms = set(original_words)
            
            # Füge direkte Synonyme hinzu
            for word in original_words:
                if word in self.synonyms:
                    expanded_terms.update(self.synonyms[word])
                    logger.debug(f"📝 Synonyme für '{word}': {self.synonyms[word]}")
            
            # Füge kontextuelle Begriffe hinzu
            for word in original_words:
                for context, terms in self.contextual_terms.items():
                    if word in terms:
                        expanded_terms.update(terms)
                        logger.debug(f"🎯 Kontext '{context}' für '{word}': {terms}")
            
            # Erstelle erweiterte Query
            expanded_query = " ".join(sorted(expanded_terms))
            
            logger.info(f"✅ Erweiterte Query: '{expanded_query}'")
            return expanded_query
            
        except Exception as e:
            logger.error(f"❌ Query-Erweiterung fehlgeschlagen: {e}")
            return query  # Fallback auf Original-Query
    
    def _extract_words(self, text: str) -> List[str]:
        """Extrahiert Wörter aus Text (min. 3 Zeichen)"""
        words = re.findall(r'\b[a-zA-ZäöüÄÖÜß]{3,}\b', text)
        return [word.lower() for word in words]
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """
        Generiert Suchvorschläge basierend auf partieller Eingabe
        
        Args:
            partial_query: Unvollständige Suchquery
            
        Returns:
            Liste von Suchvorschlägen
        """
        try:
            suggestions = set()
            partial_lower = partial_query.lower()
            
            # Finde passende Synonyme
            for term, synonyms in self.synonyms.items():
                if partial_lower in term:
                    suggestions.add(term)
                    suggestions.update(synonyms[:3])  # Max 3 Synonyme
                
                for synonym in synonyms:
                    if partial_lower in synonym:
                        suggestions.add(synonym)
                        suggestions.add(term)
            
            # Finde kontextuelle Begriffe
            for context, terms in self.contextual_terms.items():
                if partial_lower in context:
                    suggestions.update(terms[:5])  # Max 5 kontextuelle Begriffe
            
            # Sortiere und limitiere Vorschläge
            sorted_suggestions = sorted(list(suggestions))[:10]
            
            logger.debug(f"💡 Suchvorschläge für '{partial_query}': {sorted_suggestions}")
            return sorted_suggestions
            
        except Exception as e:
            logger.error(f"❌ Suchvorschläge fehlgeschlagen: {e}")
            return []
    
    def analyze_query_intent(self, query: str) -> Dict[str, any]:
        """
        Analysiert die Absicht hinter einer Suchquery
        
        Args:
            query: Suchquery
            
        Returns:
            Dictionary mit Intent-Analyse
        """
        try:
            query_lower = query.lower()
            words = self._extract_words(query_lower)
            
            intent_analysis = {
                "primary_intent": "general",
                "confidence": 0.5,
                "categories": [],
                "suggested_refinements": [],
                "detected_entities": []
            }
            
            # Erkenne primäre Absicht
            if any(word in words for word in ["fehler", "error", "problem", "bug"]):
                intent_analysis["primary_intent"] = "troubleshooting"
                intent_analysis["confidence"] = 0.8
                intent_analysis["categories"].append("Fehlerbehandlung")
                
            elif any(word in words for word in ["zeitplan", "schedule", "cron", "automation"]):
                intent_analysis["primary_intent"] = "scheduling"
                intent_analysis["confidence"] = 0.8
                intent_analysis["categories"].append("Zeitplanung")
                
            elif any(word in words for word in ["überwachung", "monitoring", "log", "alert"]):
                intent_analysis["primary_intent"] = "monitoring"
                intent_analysis["confidence"] = 0.8
                intent_analysis["categories"].append("Überwachung")
                
            elif any(word in words for word in ["config", "konfiguration", "setup", "parameter"]):
                intent_analysis["primary_intent"] = "configuration"
                intent_analysis["confidence"] = 0.8
                intent_analysis["categories"].append("Konfiguration")
                
            elif any(word in words for word in ["batch", "stream", "job", "prozess"]):
                intent_analysis["primary_intent"] = "processing"
                intent_analysis["confidence"] = 0.8
                intent_analysis["categories"].append("Datenverarbeitung")
            
            # Erkenne Entitäten
            for word in words:
                if word in ["streamworks", "powershell", "csv", "xml", "api"]:
                    intent_analysis["detected_entities"].append(word)
            
            # Generiere Verfeinerungsvorschläge
            if intent_analysis["primary_intent"] == "general":
                intent_analysis["suggested_refinements"] = [
                    "Spezifizieren Sie den Bereich (z.B. 'Batch-Verarbeitung')",
                    "Fügen Sie Kontext hinzu (z.B. 'StreamWorks Fehler')",
                    "Verwenden Sie spezifische Begriffe (z.B. 'PowerShell Script')"
                ]
            
            logger.debug(f"🎯 Intent-Analyse für '{query}': {intent_analysis}")
            return intent_analysis
            
        except Exception as e:
            logger.error(f"❌ Intent-Analyse fehlgeschlagen: {e}")
            return {"primary_intent": "general", "confidence": 0.0, "categories": [], "suggested_refinements": [], "detected_entities": []}
    
    def get_related_terms(self, term: str) -> List[str]:
        """
        Findet verwandte Begriffe zu einem Suchterm
        
        Args:
            term: Suchbegriff
            
        Returns:
            Liste verwandter Begriffe
        """
        try:
            related = set()
            term_lower = term.lower()
            
            # Direkte Synonyme
            if term_lower in self.synonyms:
                related.update(self.synonyms[term_lower])
            
            # Kontextuelle Verwandtschaft
            for context, terms in self.contextual_terms.items():
                if term_lower in terms:
                    related.update(terms)
            
            # Entferne ursprünglichen Term
            related.discard(term_lower)
            
            return sorted(list(related))
            
        except Exception as e:
            logger.error(f"❌ Verwandte Begriffe für '{term}' fehlgeschlagen: {e}")
            return []

# Global instance
intelligent_search = IntelligentSearch()