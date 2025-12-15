# StreamWorks API Referenz v2.0

## Überblick

Die StreamWorks REST API ermöglicht die programmatische Steuerung aller Systemfunktionen.

**Base URL**: `https://api.streamworks.example.com/v2`

**Authentifizierung**: Bearer Token (JWT)

## Endpunkte

### Streams

#### GET /streams
Listet alle Streams des aktuellen Mandanten.

**Query Parameter:**
- `status` (optional): Filtern nach Status (active, inactive, error)
- `tag` (optional): Filtern nach Tag
- `limit` (optional): Maximale Anzahl (Standard: 100)
- `offset` (optional): Pagination Offset

**Response:**
```json
{
  "streams": [
    {
      "id": "uuid",
      "name": "Daily-Report",
      "status": "active",
      "lastRun": "2024-01-15T08:00:00Z",
      "tags": ["reporting", "daily"]
    }
  ],
  "total": 42,
  "limit": 100,
  "offset": 0
}
```

#### POST /streams
Erstellt einen neuen Stream.

**Request Body:**
```json
{
  "name": "New-Stream",
  "description": "Beschreibung des Streams",
  "schedule": "0 8 * * MON-FRI",
  "tags": ["tag1", "tag2"],
  "jobs": []
}
```

**Response:** 201 Created mit Stream-Objekt

#### GET /streams/{id}
Ruft Details eines Streams ab.

**Response:** Stream-Objekt mit allen Jobs

#### PUT /streams/{id}
Aktualisiert einen Stream.

#### DELETE /streams/{id}
Löscht einen Stream (Soft Delete).

### Jobs

#### GET /streams/{streamId}/jobs
Listet alle Jobs eines Streams.

#### POST /streams/{streamId}/jobs
Fügt einen neuen Job hinzu.

**Job-Typen:**
- `command`: Shell-Befehl ausführen
- `script`: Script-Datei ausführen
- `sql`: SQL-Statement ausführen
- `file_transfer`: Datei kopieren/verschieben

**Request Body (Beispiel Command):**
```json
{
  "name": "Backup-Job",
  "type": "command",
  "config": {
    "command": "/opt/scripts/backup.sh",
    "workingDirectory": "/data",
    "timeout": 3600,
    "retryCount": 3,
    "retryDelay": 60
  },
  "dependencies": ["Job-A", "Job-B"]
}
```

### Ausführungen

#### POST /streams/{id}/run
Startet einen Stream manuell.

**Request Body (optional):**
```json
{
  "parameters": {
    "date": "2024-01-15",
    "mode": "full"
  }
}
```

**Response:**
```json
{
  "runId": "uuid",
  "status": "started",
  "startTime": "2024-01-15T10:30:00Z"
}
```

#### GET /runs/{runId}
Status einer Ausführung abfragen.

#### POST /runs/{runId}/cancel
Bricht eine laufende Ausführung ab.

### Tags

#### GET /tags
Listet alle verfügbaren Tags.

#### POST /streams/{id}/tags
Fügt Tags zu einem Stream hinzu.

#### DELETE /streams/{id}/tags/{tag}
Entfernt ein Tag von einem Stream.

## Fehler-Codes

| HTTP Status | Code | Beschreibung |
|-------------|------|---------------|
| 400 | INVALID_REQUEST | Ungültige Anfrage |
| 401 | UNAUTHORIZED | Nicht authentifiziert |
| 403 | FORBIDDEN | Keine Berechtigung |
| 404 | NOT_FOUND | Ressource nicht gefunden |
| 409 | CONFLICT | Konflikt (z.B. Name existiert) |
| 429 | RATE_LIMITED | Zu viele Anfragen |
| 500 | INTERNAL_ERROR | Serverfehler |

## Rate Limiting

- Standard: 100 Anfragen pro Minute
- Erhöhtes Limit auf Anfrage verfügbar
- Header `X-RateLimit-Remaining` zeigt verbleibende Anfragen

## Webhooks

StreamWorks kann Webhooks bei Events auslösen:
- `stream.started`: Stream-Ausführung gestartet
- `stream.completed`: Stream erfolgreich beendet
- `stream.failed`: Stream mit Fehler beendet
- `job.failed`: Einzelner Job fehlgeschlagen

**Webhook-Payload:**
```json
{
  "event": "stream.completed",
  "timestamp": "2024-01-15T10:45:00Z",
  "data": {
    "streamId": "uuid",
    "streamName": "Daily-Report",
    "runId": "uuid",
    "duration": 300
  }
}
```
