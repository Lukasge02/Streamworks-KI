# Listing: LangExtract-Extraktion für Streamnamen

Dieses Listing konzentriert sich ausschließlich auf neu anzulegende Stream-Konfigurationen und zeigt, wie LangExtract genau die Felder `StreamName`, `SourceAgent`, `TargetAgent`, `SourcePath` und `TargetPath` aus natürlichsprachlichen Anforderungen ableitet. Alle Beispiele sind anonymisiert und enthalten den Namensbestandteil „geck“.

## Hauptbeispiel: Erstellung eines Datei-Transfers

```python
from backend.services.ai.langextract.unified_langextract_service import UnifiedLangExtractService


async def demo_stream_creation() -> None:
    service = UnifiedLangExtractService()
    session = await service.create_session()

    user_message = (
        "Hallo SKI, bitte lege den neuen Stream 'zsw_geck_file_drop' an. Die Dateien kommen "
        "vom TestAgent1 aus dem Pfad /srv/geck/input und sollen auf TestAgent2 unter "
        "/data/geck/output landen."
    )

    response = await service.process_message(
        session_id=session.session_id,
        user_message=user_message,
    )

    print(response.extracted_stream_parameters.get("StreamName"))
    print(response.extracted_stream_parameters.get("SourceAgent"))
    print(response.extracted_stream_parameters.get("TargetAgent"))
    print(response.extracted_stream_parameters.get("SourcePath"))
    print(response.extracted_stream_parameters.get("TargetPath"))
```

```json
{
  "extracted_stream_parameters": {
    "StreamName": "zsw_geck_file_drop",
    "SourceAgent": "TestAgent1",
    "TargetAgent": "TestAgent2",
    "SourcePath": "/srv/geck/input",
    "TargetPath": "/data/geck/output"
  },
  "suggested_questions": [
    "Zu welchen Zeiten soll der Stream ausgeführt werden?"
  ]
}
```

## Few-Shot Beispiele für Stream-Erstellung

> **Eingabe:** „Hallo KI, richte bitte `zsw_geck_finance_sync` ein. Quelle ist TestAgent1 im Ordner `/mnt/geck/finance/inbox`, Ziel ist TestAgent3 unter `/mnt/geck/finance/archive`."
>
> **Erwartete Parameter:**
> - `StreamName`: `zsw_geck_finance_sync`
> - `SourceAgent`: `TestAgent1`
> - `TargetAgent`: `TestAgent3`
> - `SourcePath`: `/mnt/geck/finance/inbox`
> - `TargetPath`: `/mnt/geck/finance/archive`
>
> **Typische Folgefrage der KI:** „Soll der Stream täglich laufen? Wenn ja, zu welcher Uhrzeit?“

> **Eingabe:** „Hallo KI, bitte setze einen nächtlichen Stream `zsw_geck_analytics_push` auf. TestAgent2 liest aus `/var/geck/export`, TestAgent4 schreibt nach `/var/geck/analytics/import`."
>
> **Erwartete Parameter:**
> - `StreamName`: `zsw_geck_analytics_push`
> - `SourceAgent`: `TestAgent2`
> - `TargetAgent`: `TestAgent4`
> - `SourcePath`: `/var/geck/export`
> - `TargetPath`: `/var/geck/analytics/import`
>
> **Typische Folgefrage der KI:** „Welche Uhrzeit wünschst du für den nächtlichen Lauf?“

> **Eingabe:** „Hallo KI, für die Dokumentenablage benötigen wir `zsw_geck_docs_bridge`. Dateien starten auf TestAgent5 unter `/files/geck/docs/in`, Ziel ist TestAgent6 mit `/files/geck/docs/out`."
>
> **Erwartete Parameter:**
> - `StreamName`: `zsw_geck_docs_bridge`
> - `SourceAgent`: `TestAgent5`
> - `TargetAgent`: `TestAgent6`
> - `SourcePath`: `/files/geck/docs/in`
> - `TargetPath`: `/files/geck/docs/out`
>
> **Typische Folgefrage der KI:** „Gibt es bestimmte Wochentage oder Uhrzeiten, zu denen der Stream laufen soll?“
