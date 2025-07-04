# 🎯 SKI Prompt Management System

## 📋 Übersicht

Zentrale Verwaltung aller SKI (StreamWorks-KI) Prompts und Anweisungen für:
- **Konsistente Persona** über alle Services
- **Einfache Wartbarkeit** und Updates
- **A/B Testing** von Prompts
- **Prompt Engineering** ohne Code-Änderungen

## 📁 Struktur

```
prompts/
├── core/
│   ├── persona.yaml          # SKI Grundpersönlichkeit
│   ├── instructions.yaml     # Basis-Anweisungen
│   └── formatting.yaml       # Antwort-Formatierung
├── services/
│   ├── rag_prompts.yaml      # RAG-spezifische Prompts
│   ├── mistral_prompts.yaml  # Mistral LLM Prompts
│   └── chat_prompts.yaml     # Chat API Prompts
├── templates/
│   ├── greetings.yaml        # Begrüßungen
│   ├── fallbacks.yaml        # Fallback-Antworten
│   └── errors.yaml           # Error-Handling
└── manager.py                # Prompt Manager Service
```

## 🔧 Verwendung

```python
from app.core.prompts.manager import prompt_manager

# Lade SKI Persona
persona = prompt_manager.get_persona()

# Lade Service-spezifische Prompts
rag_prompts = prompt_manager.get_service_prompts('rag')

# Baue vollständigen Prompt
full_prompt = prompt_manager.build_prompt(
    template='mistral_rag',
    context={'user_message': 'Wie erstelle ich einen Batch-Job?'},
    persona=persona
)
```

## 🎯 Vorteile

- **Zentrale Verwaltung**: Alle Prompts an einem Ort
- **Konsistenz**: Einheitliche SKI-Persona über alle Services
- **Versionierung**: Prompt-Versionen und A/B Testing
- **Hot-Reload**: Prompt-Änderungen ohne Neustart
- **Templating**: Dynamische Prompt-Generierung