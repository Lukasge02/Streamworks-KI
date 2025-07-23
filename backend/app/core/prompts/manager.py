"""
🎯 SKI Prompt Manager
Zentrale Verwaltung aller SKI-Prompts und Templates
"""
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

class PromptManager:
    """Zentrale Verwaltung für SKI-Prompts und Templates"""
    
    def __init__(self):
        self.prompts_dir = Path(__file__).parent
        self.cache = {}
        self.version = "2.0"
        
        logger.info(f"🎯 Prompt Manager initialisiert - Version {self.version}")
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Lade YAML-Datei mit Caching"""
        cache_key = str(file_path)
        
        if cache_key not in self.cache:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.cache[cache_key] = yaml.safe_load(f)
                logger.debug(f"📁 Geladen: {file_path.name}")
            except Exception as e:
                logger.error(f"❌ Fehler beim Laden von {file_path}: {e}")
                return {}
        
        return self.cache[cache_key]
    
    @lru_cache(maxsize=32)
    def get_persona(self) -> Dict[str, Any]:
        """Lade SKI Grundpersönlichkeit"""
        persona_path = self.prompts_dir / "core" / "persona.yaml"
        return self._load_yaml(persona_path)
    
    @lru_cache(maxsize=32)
    def get_instructions(self) -> Dict[str, Any]:
        """Lade Basis-Anweisungen"""
        instructions_path = self.prompts_dir / "core" / "instructions.yaml"
        return self._load_yaml(instructions_path)
    
    def get_service_prompts(self, service_name: str) -> Dict[str, Any]:
        """Lade Service-spezifische Prompts"""
        service_path = self.prompts_dir / "services" / f"{service_name}_prompts.yaml"
        return self._load_yaml(service_path)
    
    def get_template(self, category: str, template_name: str = None) -> str:
        """Lade spezifisches Template"""
        template_path = self.prompts_dir / "templates" / f"{category}.yaml"
        templates = self._load_yaml(template_path)
        
        if template_name:
            return templates.get(template_name, "")
        
        return templates
    
    def build_prompt(self, 
                     template_type: str,
                     context: Dict[str, Any] = None,
                     include_persona: bool = True,
                     include_instructions: bool = True) -> str:
        """Baue vollständigen Prompt aus Templates"""
        
        context = context or {}
        prompt_parts = []
        
        try:
            # Persona laden
            if include_persona:
                persona = self.get_persona()
                prompt_parts.append(self._format_persona(persona))
            
            # Anweisungen laden
            if include_instructions:
                instructions = self.get_instructions()
                prompt_parts.append(self._format_instructions(instructions))
            
            # Service-spezifischen Prompt laden
            service_name = template_type.split('_')[0]  # z.B. "mistral" aus "mistral_rag"
            service_prompts = self.get_service_prompts(service_name)
            
            # Template-spezifischen Teil laden
            template_key = template_type.replace(f"{service_name}_", "")
            if template_key in service_prompts:
                template = service_prompts[template_key]
                formatted_template = template.format(**context)
                prompt_parts.append(formatted_template)
            
            final_prompt = "\n\n".join(prompt_parts)
            logger.debug(f"🎯 Prompt erstellt: {template_type} ({len(final_prompt)} Zeichen)")
            
            return final_prompt
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Erstellen des Prompts {template_type}: {e}")
            return self._get_fallback_prompt(context.get('user_message', 'Unbekannte Anfrage'))
    
    def _format_persona(self, persona: Dict[str, Any]) -> str:
        """Formatiere Persona für Prompt"""
        identity = persona.get('identity', {})
        expertise = persona.get('expertise', [])
        
        persona_text = f"""Sie sind {persona.get('name', 'SKI')}, {identity.get('role', 'Expertin')}.

UNTERNEHMEN: {identity.get('employer', 'Arvato Systems')}
SPEZIALISIERUNG: {identity.get('specialization', 'StreamWorks-Automatisierung')}

EXPERTISE:
{chr(10).join(f"- {exp}" for exp in expertise)}"""
        
        return persona_text
    
    def _format_instructions(self, instructions: Dict[str, Any]) -> str:
        """Formatiere Anweisungen für Prompt"""
        rules = instructions.get('core_rules', {})
        structure = instructions.get('response_structure', {})
        
        instructions_text = f"""GRUNDREGELN:
- {rules.get('language', 'Deutsch verwenden')}
- {rules.get('politeness', 'Höflich bleiben')}
- {rules.get('citations', 'Quellen zitieren')}

ANTWORT-FORMAT:
{structure.get('format', 'Markdown mit Emojis')}"""
        
        return instructions_text
    
    def _get_fallback_prompt(self, user_message: str) -> str:
        """Erstelle Fallback-Prompt bei Fehlern"""
        return f"""Sie sind SKI, eine StreamWorks-Expertin.
        
Benutzeranfrage: {user_message}

Antworten Sie hilfsbereit und professionell auf Deutsch."""
    
    def get_greeting(self, context: str = "main") -> str:
        """Lade passende Begrüßung"""
        greetings = self.get_template("greetings")
        
        if context in greetings:
            return greetings[context]
        
        return greetings.get("main_greeting", "👋 Hallo! Ich bin SKI, Ihre StreamWorks-Expertin.")
    
    def get_fallback(self, category: str = "general", query: str = "") -> str:
        """Lade passende Fallback-Antwort"""
        fallbacks = self.get_template("fallbacks")
        
        if category in fallbacks.get("topic_fallbacks", {}):
            return fallbacks["topic_fallbacks"][category]
        
        general_fallback = fallbacks.get("general_fallback", "")
        return general_fallback.format(query=query)
    
    def reload_cache(self):
        """Leere Cache für Hot-Reload"""
        self.cache.clear()
        self.get_persona.cache_clear()
        self.get_instructions.cache_clear()
        logger.info("🔄 Prompt Cache geleert - Hot-Reload bereit")
    
    def validate_prompts(self) -> Dict[str, bool]:
        """Validiere alle Prompt-Dateien"""
        results = {}
        
        # Prüfe Core-Dateien
        core_files = ["persona.yaml", "instructions.yaml"]
        for file in core_files:
            path = self.prompts_dir / "core" / file
            results[f"core/{file}"] = path.exists()
        
        # Prüfe Service-Dateien
        services_dir = self.prompts_dir / "services"
        if services_dir.exists():
            for service_file in services_dir.glob("*.yaml"):
                results[f"services/{service_file.name}"] = True
        
        # Prüfe Template-Dateien
        templates_dir = self.prompts_dir / "templates"
        if templates_dir.exists():
            for template_file in templates_dir.glob("*.yaml"):
                results[f"templates/{template_file.name}"] = True
        
        logger.info(f"✅ Prompt-Validierung: {sum(results.values())}/{len(results)} OK")
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiken über geladene Prompts"""
        stats = {
            "version": self.version,
            "cache_size": len(self.cache),
            "prompts_loaded": list(self.cache.keys()),
            "validation": self.validate_prompts()
        }
        
        return stats

# Global instance
prompt_manager = PromptManager()