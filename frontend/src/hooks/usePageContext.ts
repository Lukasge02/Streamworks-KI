/**
 * usePageContext Hook
 * Provides contextual suggestions and information based on current page
 */

'use client'

import { usePathname } from 'next/navigation'
import { useMemo } from 'react'

interface PageSuggestion {
  text: string
  icon?: string
  category?: 'question' | 'action' | 'help'
}

interface PageContext {
  suggestions: PageSuggestion[]
  currentPage: string
  pageTitle: string
  pageCategory: string
}

export const usePageContext = (): PageContext => {
  const pathname = usePathname()

  const pageContext = useMemo(() => {
    // Handle dynamic routes
    const isDynamicDocument = pathname.startsWith('/documents/') && pathname !== '/documents'
    const isAuthPage = pathname.startsWith('/auth/')

    if (isDynamicDocument) {
      return {
        suggestions: [
          { text: "Fasse dieses Dokument zusammen", icon: "📄", category: "action" as const },
          { text: "Extrahiere wichtige Informationen", icon: "🔍", category: "action" as const },
          { text: "Welche verwandten Dokumente gibt es?", icon: "🔗", category: "question" as const },
          { text: "Erstelle eine Zusammenfassung", icon: "📝", category: "action" as const },
          { text: "Analysiere den Inhalt", icon: "📊", category: "action" as const }
        ],
        pageTitle: "Dokumentenansicht",
        pageCategory: "documents"
      }
    }

    // Static page suggestions
    const pageMap: Record<string, Omit<PageContext, 'currentPage'>> = {
      '/dashboard': {
        suggestions: [
          { text: "Zeige mir eine Übersicht der System-Performance", icon: "📊", category: "question" },
          { text: "Wie viele Dokumente wurden heute verarbeitet?", icon: "📈", category: "question" },
          { text: "Gibt es aktuelle System-Warnungen?", icon: "⚠️", category: "question" },
          { text: "Starte einen neuen Workflow", icon: "🚀", category: "action" },
          { text: "Zeige mir die neuesten Aktivitäten", icon: "🕐", category: "question" }
        ],
        pageTitle: "Dashboard",
        pageCategory: "overview"
      },
      '/documents': {
        suggestions: [
          { text: "Hilf mir beim Organisieren meiner Dokumente", icon: "📁", category: "help" },
          { text: "Welche Dokumente sind am relevantesten?", icon: "⭐", category: "question" },
          { text: "Wie kann ich die Suche optimieren?", icon: "🔍", category: "help" },
          { text: "Lade ein neues Dokument hoch", icon: "📤", category: "action" },
          { text: "Erstelle eine neue Sammlung", icon: "📚", category: "action" }
        ],
        pageTitle: "Dokumente",
        pageCategory: "documents"
      },
      '/langextract': {
        suggestions: [
          { text: "Erkläre mir das LangExtract System", icon: "🤖", category: "help" },
          { text: "Wie erstelle ich einen neuen Parameter-Extraction Job?", icon: "⚙️", category: "help" },
          { text: "Welche Job-Typen werden unterstützt?", icon: "📋", category: "question" },
          { text: "Starte eine neue Parameter-Extraktion", icon: "🚀", category: "action" },
          { text: "Zeige mir Beispiele für Job-Templates", icon: "📝", category: "question" }
        ],
        pageTitle: "LangExtract",
        pageCategory: "ai-tools"
      },
      '/xml': {
        suggestions: [
          { text: "Hilf mir beim Erstellen einer XML-Vorlage", icon: "📄", category: "help" },
          { text: "Wie funktioniert die Parameter-Zuordnung?", icon: "🔗", category: "help" },
          { text: "Zeige mir XML-Template Beispiele", icon: "💡", category: "question" },
          { text: "Erstelle eine neue XML-Vorlage", icon: "📝", category: "action" },
          { text: "Validiere meine XML-Struktur", icon: "✅", category: "action" }
        ],
        pageTitle: "XML Generator",
        pageCategory: "tools"
      },
      '/chat': {
        suggestions: [
          { text: "Was kann SKI alles für mich tun?", icon: "🤔", category: "question" },
          { text: "Zeige mir alle verfügbaren Funktionen", icon: "🔧", category: "question" },
          { text: "Hilf mir bei einem spezifischen Problem", icon: "❓", category: "help" },
          { text: "Erkläre mir wie Streamworks funktioniert", icon: "📚", category: "help" }
        ],
        pageTitle: "Chat",
        pageCategory: "chat"
      },
      '/upload': {
        suggestions: [
          { text: "Welche Dateiformate werden unterstützt?", icon: "📎", category: "question" },
          { text: "Wie funktioniert die automatische Verarbeitung?", icon: "⚙️", category: "help" },
          { text: "Optimiere meine Upload-Einstellungen", icon: "🔧", category: "action" },
          { text: "Zeige mir Upload-Verlauf", icon: "📋", category: "question" }
        ],
        pageTitle: "Upload",
        pageCategory: "tools"
      },
      '/profile': {
        suggestions: [
          { text: "Wie kann ich meine Einstellungen anpassen?", icon: "⚙️", category: "help" },
          { text: "Zeige mir meine Nutzungsstatistiken", icon: "📊", category: "question" },
          { text: "Wie ändere ich mein Passwort?", icon: "🔐", category: "help" },
          { text: "Exportiere meine Daten", icon: "📤", category: "action" }
        ],
        pageTitle: "Profil",
        pageCategory: "settings"
      }
    }

    // Auth pages
    if (isAuthPage) {
      return {
        suggestions: [
          { text: "Ich habe Probleme beim Anmelden", icon: "🔐", category: "help" },
          { text: "Wie erstelle ich einen neuen Account?", icon: "👤", category: "help" },
          { text: "Passwort vergessen - was tun?", icon: "❓", category: "help" }
        ],
        pageTitle: "Anmeldung",
        pageCategory: "auth"
      }
    }

    // Fallback for unknown pages
    return pageMap[pathname] || {
      suggestions: [
        { text: "Was kann SKI für dich tun?", icon: "🤖", category: "question" },
        { text: "Brauchst du Hilfe bei Streamworks?", icon: "❓", category: "help" },
        { text: "Zeige mir alle verfügbaren Funktionen", icon: "🔧", category: "question" },
        { text: "Erkläre mir das System", icon: "📚", category: "help" },
        { text: "Starte einen neuen Workflow", icon: "🚀", category: "action" }
      ],
      pageTitle: "Streamworks",
      pageCategory: "general"
    }
  }, [pathname])

  return {
    ...pageContext,
    currentPage: pathname
  }
}

export default usePageContext